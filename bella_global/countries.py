COUNTRIES_TYPES = (
    ('bangladesh', 'Bangladesh'),
    ('india', 'India'),
    ('uk', 'UK'),
    ('russia', 'Russia'),
    ('uae', 'UAE'),
    ('korea', 'Korea'),
    ('japan', 'Japan'),
    ('canada', 'Canada'),
    ('america', 'America'),
    ('china', 'China'),
    ('belgium', 'Belgium'),
    ('france', 'France'),
    ('hongkong', 'HongKong'),
    ('italy', 'Italy'),
    ('nederlands', 'Nederlands'),
    ('turkey', 'Turkey'),
    ('pan_african', 'Pan African'),
)


def get_country_dropdown_data(selected_code=None):
    """
    Returns a list of dictionaries formatted for searchable dropdowns.
    Identifies the currently selected country.
    """
    COUNTRIES_TYPES = (
        ('bangladesh', 'Bangladesh'), ('india', 'India'), ('uk', 'UK'),
        ('russia', 'Russia'), ('uae', 'UAE'), ('korea', 'Korea'),
        ('japan', 'Japan'), ('canada', 'Canada'), ('america', 'America'),
        ('china', 'China'), ('belgium', 'Belgium'), ('france', 'France'),
        ('hongkong', 'HongKong'), ('italy', 'Italy'), ('nederlands', 'Nederlands'),
        ('turkey', 'Turkey'), ('pan_african', 'Pan African'),
    )
    
    return [
        {
            'id': code,
            'text': name,
            'selected': code == selected_code
        }
        for code, name in COUNTRIES_TYPES
    ]