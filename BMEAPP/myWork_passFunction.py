def get_myWorkpass_data(user_group, worklist):
    sidebar_map = {
        'BMEADMIN': 'sidebar.html',
        'BMESTAFF': 'sidebarbmestaff.html',
        'NURSING': 'sidebarNurse.html',
        'MANAGEMENT': 'sidebarAdmin.html'
    }
    
    sidebar_template = sidebar_map.get(user_group)

    group_data = {
        'BMEADMIN': {'sidebar_template': sidebar_template, 'hovered4': "hovered", 'worklist': worklist},
        'BMESTAFF': {'sidebar_template': sidebar_template, 'hovered4': "hovered", 'worklist': worklist},
        'NURSING': {'sidebar_template': sidebar_template, 'hovered4': "hovered", 'worklist': worklist},
        'MANAGEMENT': {'sidebar_template': sidebar_template, 'hovered4': "hovered", 'worklist': worklist},
    }

    return group_data.get(user_group)