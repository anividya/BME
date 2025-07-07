def getAssetpassData(user_group,asset,installation_docs,purchase_docs,training_docs,works,work_docs):
    sidebar_map = {
        'BMEADMIN': 'sidebar.html',
        'BMESTAFF': 'sidebarbmestaff.html',
        'NURSING': 'sidebarNurse.html',
        'MANAGEMENT': 'sidebarAdmin.html'
    }

    


    sidebar_template = sidebar_map.get(user_group)

    group_data = {
        'BMEADMIN': {'sidebar_template': sidebar_template, 'hovered1': "hovered",'asset': asset,'installation_docs': installation_docs,'purchase_docs': purchase_docs,'training_docs': training_docs,'worklist': works,'work_docs':work_docs},
        'BMESTAFF': {'sidebar_template': sidebar_template, 'hovered1': "hovered",'asset': asset,'installation_docs': installation_docs,'purchase_docs': purchase_docs,'training_docs': training_docs,'works': works},
        'NURSING': {'sidebar_template': sidebar_template, 'hovered1': "hovered",'asset': asset,'installation_docs': installation_docs,'purchase_docs': purchase_docs,'training_docs': training_docs,'works': works},
        'MANAGEMENT': {'sidebar_template': sidebar_template, 'hovered1': "hovered",'asset': asset,'installation_docs': installation_docs,'purchase_docs': purchase_docs,'training_docs': training_docs,'works': works},
    }

    return group_data.get(user_group)