{
    'name': 'Learning Management Toolkit',
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
    'depends': [
        'base',
        'mail',
        'website', 
        'website_mail',
        'document',
        'web_tree_many2one_clickable',
        'ees_tree_no_open',
        'formio',
        # 'odoo-debrand',
    ],
    'demo': [
    ],
    'data': [
        'security/lms_security.xml',
        'security/ir.model.access.csv',
        'views/lms_view.xml',
        'views/lms_student_view.xml',
        'views/lms_menu.xml',
        'views/lms_templates.xml',
        'views/lms_formio.xml',
    ],
    'qweb': [

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
