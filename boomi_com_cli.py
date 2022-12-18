from utils import init_log, inquire, read_yaml, group_by
from boomi_com_api import BoomiAPI
from rich import print_json


if __name__ == '__main__':
    init_log(__file__)
    
    api = BoomiAPI(**inquire("Account", {cred["id"]: cred for cred in read_yaml("boomi.yml")}))
    
    match inquire("Type", ["User", "Project"]):
        case "User":
            user_roles, federations, roles, folders = api.multi_query(dict(AccountUserRole=None, AccountUserFederation=None, Role=None, Folder=None))
            m_uroles, m_roles, m_fed = group_by(user_roles, "userId"), group_by(roles, "id"), group_by(federations, "userId", False)
            match inquire("Action", ["Check"]):
                case "Check":
                    print_json(data=[{
                        k:v for k,v in m_uroles[user][0].items() if k in ["userId","firstName","lastName"]
                    } | {
                        k: [r["name"] for r in v]
                    for k,v in group_by([r for r in roles if r["id"] in [ur["roleId"] for ur in m_uroles[user]]], "Description").items()} | dict(
                        # federationId = m_fed[user][0]["federationId"] if user in m_fed else None,
                        federationId = m_fed[user]["federationId"] if user in m_fed else None,
                        folders      = [f["fullPath"] for f in folders if any([fr["id"] in [ur["roleId"] for ur in m_uroles[user]] and m_roles[fr["id"]][0]["Description"] == "USER" for fr in f["PermittedRoles"]["RoleReference"]])]
                    ) for user in inquire("User(s)", m_uroles.keys(), True)])
        case "Project":
            user_roles, roles = api.multi_query(dict(AccountUserRole=None, Role=None))
            projects = inquire("Project(s)", {r["name"]:r  for r in roles if r["Description"] == "PROJECT"}, True)
            print_json(data={project["name"]: [u["userId"] for u in user_roles if u["roleId"] == project["id"]] for project in projects})