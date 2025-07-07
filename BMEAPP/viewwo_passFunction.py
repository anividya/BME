from django.contrib.auth.models import Group
from django.shortcuts import render
def get_woviewpass_data(user_group, worklist):

    group = Group.objects.get(name='BMESTAFF')
    users_in_group = group.user_set.all()

    sidebar_map = {
        'BMEADMIN': 'sidebar.html',
        'BMESTAFF': 'sidebarbmestaff.html',
        'NURSING': 'sidebarNurse.html',
        'MANAGEMENT': 'sidebarAdmin.html'
    }
    
    sidebar_template = sidebar_map.get(user_group)

    group_data = {
        'BMEADMIN': {'sidebar_template': sidebar_template, 'hovered3': "hovered", 'worklist': worklist,'bmestaff_users': users_in_group},
        'BMESTAFF': {'sidebar_template': sidebar_template, 'hovered3': "hovered", 'worklist': worklist},
        'NURSING': {'sidebar_template': sidebar_template, 'hovered3': "hovered", 'worklist': worklist},
        'MANAGEMENT': {'sidebar_template': sidebar_template, 'hovered2': "hovered", 'worklist': worklist},
    }

    return group_data.get(user_group)

def woUserapprovepass_data(user_group, worklist):

    sidebar_map = {
        'BMEADMIN': 'sidebar.html',
        'BMESTAFF': 'sidebarbmestaff.html',
        'NURSING': 'sidebarNurse.html',
        'MANAGEMENT': 'sidebarAdmin.html'
    }
    
    sidebar_template = sidebar_map.get(user_group)

    group_data = {
        #'BMEADMIN': {'sidebar_template': sidebar_template, 'hovered3': "hovered", 'worklist': worklist,},
        #'BMESTAFF': {'sidebar_template': sidebar_template, 'hovered3': "hovered", 'worklist': worklist},
        'NURSING': {'sidebar_template': sidebar_template, 'hovered4': "hovered", 'worklist': worklist},
        #'MANAGEMENT': {'sidebar_template': sidebar_template, 'hovered3': "hovered", 'worklist': worklist},
    }

    return group_data.get(user_group)