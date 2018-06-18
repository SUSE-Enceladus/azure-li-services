schema = {
    'version': {
        'required': True,
        'type': 'string'
    },
    'instance_type': {
        'required': True,
        'type': 'string',
        'nullable': False,
        'regex': '^(LargeInstance|VeryLargeInstance)$'
    },
    'sku': {
        'required': True,
        'type': 'string'
    },
    'machine_constraints': {
        'required': False,
        'type': 'dict',
        'schema': {
            'min_cores': {
                'required': False,
                'type': 'number'
            },
            'min_memory': {
                'required': False,
                'type': 'string'
            }
        }
    },
    'networking': {
        'required': True,
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'interface': {
                    'required': True,
                    'type': 'string'
                },
                'vlan': {
                    'required': False,
                    'type': 'number'
                },
                'ip': {
                    'required': True,
                    'type': 'string'
                },
                'gateway': {
                    'required': False,
                    'type': 'string'
                },
                'subnet_mask': {
                    'required': True,
                    'type': 'string'
                }
            }
        }
    },
    'storage': {
        'required': False,
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'file_system': {
                    'required': False,
                    'type': 'string'
                },
                'min_size': {
                    'required': False,
                    'type': 'string'
                },
                'device': {
                    'required': True,
                    'type': 'string'
                },
                'mount': {
                    'required': True,
                    'type': 'string'
                },
                'mount_options': {
                    'required': False,
                    'type': 'list',
                    'nullable': False
                }
            }
        }
    },
    'credentials': {
        'required': True,
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'username': {
                    'required': True,
                    'type': 'string'
                },
                'shadow_hash': {
                    'required': False,
                    'type': 'string'
                },
                'ssh-key': {
                    'required': False,
                    'type': 'string'
                },
                'id': {
                    'required': False,
                    'type': 'number'
                },
                'group': {
                    'required': False,
                    'type': 'string'
                },
                'home_dir': {
                    'required': False,
                    'type': 'string'
                }
            }
        }
    },
    'packages': {
        'required': False,
        'type': 'dict',
        'schema': {
            'repository_name': {
                'required': True,
                'type': 'string'
            },
            'directory': {
                'required': True,
                'type': 'list',
                'nullable': False
            }
        }
    },
    'call': {
        'required': False,
        'type': 'string'
    }
}
