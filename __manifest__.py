{
    'name': 'CMS Assignment',
    'version': '16.0.1.0.0',
    'author': 'Abdullah',
    'sequence': '-1',
    'category': 'CMS Assignment for Students and Teachers',
    'license': "AGPL-3",
    'Summary': 'CMS Assignment for Students and Teachers',
    'images': ['static/description/icon.jpg'],
    'depends': ['base'],
    'data': [
        'security/cms_assignment_security.xml',
        'security/ir.model.access.csv', 
        'views/cms_assignment_view.xml',
        'views/cms_assignment_menu.xml',
        ],
        
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
