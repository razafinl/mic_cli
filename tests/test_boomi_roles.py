import pytest
from utils import read_yaml, group_by
from boomi_com_api import BoomiAPI

apis = [BoomiAPI(**cred) for cred in read_yaml("boomi.yml")]
apis = {api.id: api for api in apis}

user_roles, roles = [{
    domain: group_by(api.query(obj), key, obj not in ["Role"])
for domain, api in apis.items()} for obj, key in dict(
    AccountUserRole = "userId",
    Role            = "id"
).items()]

users = {
    account: [{
            k:v
        for k,v in u_roles[0].items() if k in ["userId","firstName","lastName"] } | {
            k: [r["name"] for r in v]
        for k,v in group_by([r for r in roles[account].values() if r["id"] in [ur["roleId"] for ur in u_roles]], "Description").items()}
    for u_roles in user_roles[account].values()]
for account in apis.keys()}

@pytest.mark.parametrize("account", apis.keys())
def test_credentials(account: str):
    assert apis[account].get("Account", account)["accountId"] == account

@pytest.mark.parametrize("account", apis.keys())
def test_no_undescribed_role(account: str):
    assert all(["Description" in role for role in roles[account].values()])

@pytest.mark.parametrize("account", apis.keys())
def test_user_role(account: str):
    assert all(["PROJECT" in user for user in users[account]])