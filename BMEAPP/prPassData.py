def pr_pass_data(user_group,prdata):
    sidebar_map = {
        'BMEADMIN': 'sidebar.html',
        'BMESTAFF': 'sidebarbmestaff.html',
        'NURSING': 'sidebarNurse.html',
        'MANAGEMENT': 'sidebarAdmin.html'
    }

    sidebar_template = sidebar_map.get(user_group)

    group_data = {
        'BMEADMIN': {'sidebar_template': sidebar_template, 'hovered7': "hovered",'prdata':prdata},
        'BMESTAFF': {'sidebar_template': sidebar_template, 'hovered7': "hovered",'prdata':prdata},
        'NURSING': {'sidebar_template': sidebar_template, 'hovered7': "hovered",'prdata':prdata},
        'MANAGEMENT': {'sidebar_template': sidebar_template, 'hovered4': "hovered",'prdata':prdata},
    }

    return group_data.get(user_group)