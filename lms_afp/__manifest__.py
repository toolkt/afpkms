{
    'name': 'Learning Management AFP',
    'version' : '0.1',    
    'sequence': 100,
    'category': 'Human Resources',
    'website' : 'http://www.toolkt.com',
    'summary': 'Learning Management System',
    'version': '1.0',
    'description': """
Human Resources Management
==========================
LMS Custom Modules
        """,
    'author': 'Toolkt Inc',
    'depends': ['lms'],
    'demo': [
    ],
    'data': [
        'security/lms_security.xml',
        'security/ir.model.access.csv',
        'views/lms_view.xml',
        'views/lms_menu.xml',
    ],
    'qweb': [

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
