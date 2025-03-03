#
# Copyright 2019 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

# Import common Python modules as needed
import os.path
import sys
import logging
import json
from datetime import datetime, timedelta

logging.basicConfig(filename='log/plugin.log',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

logging.debug("main: begin")

# PermissionApi
#     - List globalPermissions

# RoleApi
#     RoleView
#         - String name
#         - Set permissions
#         - Set<PrincipalView> principals

#     PrincipalView
#         - String fullname
#         - String username

# FolderApi
#     TeamView getTeams(folder.id)
#         - String id
#         - String teamName
#         - List<TeamMemberView> members
#         - List permissions

#     TeamMemberView
#         - String fullName
#         - String name
#         - MemberType type

#     MemberType
#         - PRINCIPAL
#         - ROLE

# UserApi
#     UserAccount
#         - String dateFormat
#         - String email
#         - Integer firstDayOfWeek
#         - String fullName
#         - Date lastActive
#         - String timeFormat
#         - String username
#         - boolean loginAllowed

# EXAMPLE OUTPUT...

# Process Users ----------------------
# FYI: parameters are..  String email, String fullName, Boolean loginAllowed, Boolean external, Date lastActiveAfter, Date lastActiveBefore, Long page, Long resultsPerPage
user_obj_list = userApi.findUsers(None, None, None, None, None, None, None, None)

users = {}
for user_obj in user_obj_list:
    user = {}
    user['fullName'] = user_obj.fullName
    user['email'] = user_obj.email
    user['loginAllowed'] = user_obj.loginAllowed
    user['lastActive'] = user_obj.lastActive
    user['roles'] = {}
    user['folders'] = {}
    users[user_obj.username] = user

# augment users with roles
roles = rolesApi.getRoles(0, 1000)

for role in roles:
    for principal in role.principals:       
        role_obj = {}
        # role_obj['name'] = role.name
        role_obj['permissions'] = []
        for pem in role.permissions:
            role_obj['permissions'].append(pem)

        users[principal.username]['roles'][role.name] = role_obj

# Process Folders -------------------
rootFolders = folderApi.listRoot(0, 1000, 1, True)

def add_folder(user_folders, folder_obj):
    user_folders[folder_obj.title] = {}
    user_folders[folder_obj.title]['permissions'] = []
    for pem in team_obj.permissions:
        user_folders[folder_obj.title]['permissions'].append(pem)

folders = []
for folder_obj in rootFolders:
    # get teams for the folder
    teams = folderApi.getTeams(folder_obj.id)

    # iterate over teams in this folder
    for team_obj in teams:
        # iterate over members in this team
        for member_obj in team_obj.members:
            # team members may be principals or roles
            # for roles, the team member name is the role
            if str(member_obj.type) == 'PRINCIPAL':
                # add folder to user
                add_folder(users[member_obj.name]['folders'], folder_obj)

            elif str(member_obj.type) == 'ROLE':
                # check for users with this role
                for k in users:
                    user = users[k]
                    if member_obj.name in user['roles']:
                        # this user has role that matches the team member name, add folder
                        add_folder(user['folders'], folder_obj)

# form response
response.statusCode = 200
response.entity = {
    "users": users
}
