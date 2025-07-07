def get_wopass_data(user_group, assets):
    sidebar_map = {
        'BMEADMIN': 'sidebar.html',
        'BMESTAFF': 'sidebarbmestaff.html',
        'NURSING': 'sidebarNurse.html',
        'MANAGEMENT': 'sidebarAdmin.html'
    }
    
    sidebar_template = sidebar_map.get(user_group)

    group_data = {
        'BMEADMIN': {'sidebar_template': sidebar_template, 'hovered2': "hovered"},
        'BMESTAFF': {'sidebar_template': sidebar_template, 'hovered2': "hovered", 'assets': assets},
        'NURSING': {'sidebar_template': sidebar_template, 'hovered2': "hovered", 'assets': assets},
        'MANAGEMENT': {'sidebar_template': sidebar_template, 'hovered2': "hovered", 'assets': assets},
    }

    return group_data.get(user_group)