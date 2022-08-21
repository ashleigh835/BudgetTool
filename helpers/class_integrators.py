def parse_supported_providers(Transaction) -> list:
    return dict((i,j) for i,j in enumerate(Transaction._supported_providers))  