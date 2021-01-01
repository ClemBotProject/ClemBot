def command_help(doc):
    def help_inner(func):
        func.help = doc
        return func
    return help_inner