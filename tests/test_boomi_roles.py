import pytest
from utils import read_yaml, group_by
from boomi_com_api import BoomiAPI

apis = [BoomiAPI(**cred) for cred in read_yaml("boomi.yml")]
apis = {api.id: api for api in apis}

obj_list = ["AccountUserRole", "Role", "AccountUserFederation", "Folder"]
objects = {
    account: dict(zip(obj_list, api.multi_query({obj:None for obj in obj_list})))
    for account, api in apis.items()
}
for values in objects.values():
    for obj, key in dict(AccountUserRole = "userId", AccountUserFederation = "userId", Role = "id").items():
        values[obj] = group_by(values[obj], key, obj not in ["AccountUserFederation", "Role"])
        
users = {
    account: { user_id: {
            k:v
        for k,v in u_roles[0].items() if k in ["userId","firstName","lastName"] } | {
            k: [r["name"] for r in v]
        for k,v in group_by([r for r in objs["Role"].values() if r["id"] in [ur["roleId"] for ur in u_roles]], "Description").items()} | dict(
            federation = objs["AccountUserFederation"][user_id]["federationId"] if user_id in objs["AccountUserFederation"] else None,
            folders    = [f["fullPath"] for f in objs["Folder"] if any([fr["id"] in [ur["roleId"] for ur in u_roles] and objs["Role"][fr["id"]]["Description"] == "USER" for fr in f["PermittedRoles"]["RoleReference"]])]
        )
    for user_id, u_roles in objs["AccountUserRole"].items() }
for account, objs in objects.items()}

@pytest.mark.parametrize("account", apis.keys())
def test_credentials(account: str):
    assert apis[account].get("Account", account)["accountId"] == account

@pytest.mark.parametrize("account", apis.keys())
def test_no_undescribed_role(account: str):
    assert all(["Description" in role for role in objects[account]["Role"].values()])

@pytest.mark.parametrize("account", apis.keys())
def test_user_role(account: str):
    assert not [user_id for user_id, user in users[account].items() if "PROJECT" not in user]

@pytest.mark.parametrize("account", apis.keys())
def test_unassigned_role(account: str):
    assigned_role_ids = {role["roleId"] for roles in objects[account]["AccountUserRole"].values() for role in roles}
    assert not [role["name"] for role_id, role in objects[account]["Role"].items() if role_id not in assigned_role_ids]    