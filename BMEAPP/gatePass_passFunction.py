def get_gatepass_data(user_group,gatepass):
    sidebar_map = {
        'BMEADMIN': 'sidebar.html',
        'BMESTAFF': 'sidebarbmestaff.html',
        'NURSING': 'sidebarNurse.html',
        'MANAGEMENT': 'sidebarAdmin.html'
    }

    uoq = [
        {"id": "Piece", "name": "Piece"},
        {"id": "Packet", "name": "Packet"},
        {"id": "Box", "name": "Box"}
        ]
    gttype = [
        {"id": "RETURNABLE", "name": "RETURNABLE"},
        {"id": "NON-RETURNABLE", "name": "NON-RETURNABLE"},
        ]
    sidebar_template = sidebar_map.get(user_group)

    group_data = {
        'BMEADMIN': {'sidebar_template': sidebar_template, 'hovered5': "hovered",'gate':gatepass, 'uoq':uoq,'gttypes':gttype},
        'BMESTAFF': {'sidebar_template': sidebar_template, 'hovered5': "hovered",'gate':gatepass,'uoq':uoq,'gttype':gttype},
        'NURSING': {'sidebar_template': sidebar_template, 'hovered5': "hovered",'gate':gatepass,'uoq':uoq,'gttype':gttype},
        'MANAGEMENT': {'sidebar_template': sidebar_template, 'hovered3': "hovered",'gate':gatepass,'uoq':uoq,'gttype':gttype},
    }

    return group_data.get(user_group)