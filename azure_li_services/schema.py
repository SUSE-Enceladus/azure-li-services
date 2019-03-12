schema = {
    'version': {
        'required': True,
        'type': 'string'
    },
    'instance_type': {
        'required': True,
        'type': 'string',
        'nullable': False,
        'regex': '^(LargeInstance|VeryLargeInstance|VeryLargeInstanceGen3)$'
    },
    'sku': {
        'required': True,
        'type': 'string'
    },
    'hostname': {
        'required': False,
        'type': 'string'
    },
    'crash_dump': {
        'required': False,
        'type': 'dict',
        'schema': {
            'activate': {
                'required': False,
                'type': 'boolean'
            },
            'crash_kernel_high': {
                'required': False,
                'type': 'number'
            },
            'crash_kernel_low': {
                'required': False,
                'type': 'number'
            }
        }
    },
    'stonith': {
        'required': False,
        'type': 'dict',
        'schema': {
            'initiatorname': {
                'required': True,
                'nullable': False,
                'type': 'string'
            },
            'ip': {
                'required': True,
                'nullable': False,
                'type': 'string'
            }
        }
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
                    'type': 'string',
                    'nullable': False
                },
                'vlan': {
                    'required': False,
                    'type': 'number'
                },
                'vlan_mtu': {
                    'required': False,
                    'type': 'number',
                    'nullable': False
                },
                'ip': {
                    'required': False,
                    'type': 'string',
                    'nullable': False
                },
                'gateway': {
                    'required': False,
                    'type': 'string',
                    'nullable': False
                },
                'subnet_mask': {
                    'required': False,
                    'type': 'string',
                    'nullable': False
                },
                'mtu': {
                    'required': False,
                    'type': 'number',
                    'nullable': False
                },
                'bonding_slaves': {
                    'required': False,
                    'type': 'list',
                    'nullable': False
                },
                'bonding_options': {
                    'required': False,
                    'type': 'list',
                    'nullable': False
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
                'require_password_change': {
                    'required': False,
                    'type': 'boolean'
                },
                'shadow_hash': {
                    'required': False,
                    'type': 'string'
                },
                'ssh-key': {
                    'required': False,
                    'type': 'string'
                },
                'ssh-private-key': {
                    'required': False,
                    'type': 'string'
                },
                'id': {
                    'required': False,
                    'type': 'number'
                },
                'group': {
                    'required': False,
                    'type': 'dict',
                    'schema': {
                        'name': {
                            'required': True,
                            'type': 'string',
                            'nullable': False
                        },
                        'id': {
                            'required': False,
                            'type': 'number'
                        }
                    }
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
            'repository': {
                'type': 'list',
                'required': False,
                'nullable': False,
                'schema': {
                    'type': 'dict',
                    'schema': {
                        'name': {
                            'required': True,
                            'type': 'string',
                            'nullable': False
                        },
                        'source': {
                            'required': True,
                            'type': 'string',
                            'nullable': False
                        },
                        'source_prefix': {
                            'required': False,
                            'type': 'string',
                            'nullable': False
                        },
                        'install': {
                            'required': False,
                            'type': 'list',
                            'nullable': False
                        }
                    }
                }
            },
            'raw': {
                'type': 'dict',
                'required': False,
                'nullable': False,
                'schema': {
                    'name': {
                        'type': 'string',
                        'required': True,
                        'nullable': False
                    },
                    'directory': {
                        'type': 'list',
                        'required': True,
                        'nullable': False
                    }
                }
            }
        }
    },
    'call': {
        'required': False,
        'type': 'string'
    }
}
