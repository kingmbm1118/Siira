def get_cultural_context(nationality):
    # This function provides cultural context information based on nationality.
    # It includes the work week structure, communication style, and important cultural practices or holidays.
    
    contexts = {
        "United States": {
            "work_week": "Monday to Friday, with Saturday and Sunday as typical weekend days.",
            "communication_style": "Direct and informal. Emphasis on efficiency, individuality, and getting to the point.",
            "special_occasions": ["Christmas", "Independence Day", "Thanksgiving"],
            "cultural_values": "Individualism, freedom, innovation."
        },
        "Japan": {
            "work_week": "Monday to Friday, with Saturday and Sunday as typical weekend days. Overtime is common and expected.",
            "communication_style": "Indirect and formal. Emphasis on politeness, harmony, and saving face.",
            "special_occasions": ["New Year's (Shogatsu)", "Golden Week", "Obon Festival"],
            "cultural_values": "Respect, harmony, group over individual."
        },
        "United Arab Emirates": {
            "work_week": "Sunday to Thursday, with Friday and Saturday as typical weekend days.",
            "communication_style": "Relatively indirect. Emphasis on relationship-building, respect for hierarchy, and maintaining harmony.",
            "special_occasions": ["Eid al-Fitr", "Eid al-Adha", "National Day (December 2)"],
            "cultural_values": "Family, hospitality, respect for tradition and religion."
        },
        "Saudi Arabia": {
            "work_week": "Sunday to Thursday, with Friday and Saturday as weekend days.",
            "communication_style": "Indirect and formal, with emphasis on respect, honor, and relationship-building.",
            "special_occasions": ["Eid al-Fitr", "Eid al-Adha", "National Day (September 23)"],
            "cultural_values": "Religion, family, hospitality, tradition."
        },
        "Egypt": {
            "work_week": "Sunday to Thursday, with Friday and Saturday as weekend days.",
            "communication_style": "Indirect, with a focus on building trust and relationships, often emotional and expressive.",
            "special_occasions": ["Eid al-Fitr", "Eid al-Adha", "Revolution Day (July 23)", "Ramadan"],
            "cultural_values": "Family, respect for elders, religion, national pride."
        },
        "Jordan": {
            "work_week": "Sunday to Thursday, with Friday and Saturday as weekend days.",
            "communication_style": "Indirect, formal, with a focus on respect for hierarchy and relationship-building.",
            "special_occasions": ["Eid al-Fitr", "Eid al-Adha", "Independence Day (May 25)", "Ramadan"],
            "cultural_values": "Hospitality, family, respect for tradition, generosity."
        },
        "Lebanon": {
            "work_week": "Monday to Friday, with Saturday as a half-day in some industries. Sunday is a rest day.",
            "communication_style": "Varied – can be both direct and indirect depending on the context. Emphasis on personal relationships.",
            "special_occasions": ["Eid al-Fitr", "Eid al-Adha", "Independence Day (November 22)", "Christmas"],
            "cultural_values": "Family, diversity, resilience, celebration."
        },
        "Morocco": {
            "work_week": "Monday to Friday, with Saturday as a half-day in some industries. Sunday is a rest day.",
            "communication_style": "Indirect, with a focus on politeness and respect, especially towards elders.",
            "special_occasions": ["Eid al-Fitr", "Eid al-Adha", "Throne Day (July 30)", "Ramadan"],
            "cultural_values": "Religion, family, hospitality, respect for elders."
        },
        "Algeria": {
            "work_week": "Sunday to Thursday, with Friday and Saturday as weekend days.",
            "communication_style": "Indirect, with emphasis on respect for hierarchy and tradition, and relationship-building.",
            "special_occasions": ["Eid al-Fitr", "Eid al-Adha", "Revolution Day (November 1)", "Ramadan"],
            "cultural_values": "Family, hospitality, respect for tradition and elders, national pride."
        },
        "Kuwait": {
            "work_week": "Sunday to Thursday, with Friday and Saturday as weekend days.",
            "communication_style": "Indirect, formal, with emphasis on respect and hierarchy, especially in business.",
            "special_occasions": ["Eid al-Fitr", "Eid al-Adha", "National Day (February 25)", "Ramadan"],
            "cultural_values": "Religion, family, respect for tradition, generosity."
        },
        "Qatar": {
            "work_week": "Sunday to Thursday, with Friday and Saturday as weekend days.",
            "communication_style": "Indirect, formal, with a strong focus on respect and relationship-building.",
            "special_occasions": ["Eid al-Fitr", "Eid al-Adha", "National Day (December 18)", "Ramadan"],
            "cultural_values": "Family, religion, respect for authority, hospitality."
        },
        "Oman": {
            "work_week": "Sunday to Thursday, with Friday and Saturday as weekend days.",
            "communication_style": "Indirect and formal, with an emphasis on respect and relationship-building.",
            "special_occasions": ["Eid al-Fitr", "Eid al-Adha", "National Day (November 18)", "Ramadan"],
            "cultural_values": "Hospitality, respect for tradition, religion, family."
        },
        "Tunisia": {
            "work_week": "Monday to Friday, with Saturday as a half-day in some industries. Sunday is a rest day.",
            "communication_style": "Indirect, with emphasis on formality, respect, and maintaining relationships.",
            "special_occasions": ["Eid al-Fitr", "Eid al-Adha", "Independence Day (March 20)", "Ramadan"],
            "cultural_values": "Family, respect for elders, religion, national pride."
        },
        "Bahrain": {
            "work_week": "Sunday to Thursday, with Friday and Saturday as weekend days.",
            "communication_style": "Indirect, formal, with an emphasis on relationship-building and respect for hierarchy.",
            "special_occasions": ["Eid al-Fitr", "Eid al-Adha", "National Day (December 16)", "Ramadan"],
            "cultural_values": "Religion, family, hospitality, respect for tradition."
        },
        "Iraq": {
            "work_week": "Sunday to Thursday, with Friday and Saturday as weekend days.",
            "communication_style": "Indirect, with a focus on politeness and relationship-building. Emotionally expressive in personal contexts.",
            "special_occasions": ["Eid al-Fitr", "Eid al-Adha", "Republic Day (July 14)", "Ramadan"],
            "cultural_values": "Family, respect for elders, religion, hospitality."
        },
        "Syria": {
            "work_week": "Sunday to Thursday, with Friday and Saturday as weekend days.",
            "communication_style": "Indirect, formal, with emphasis on politeness, respect for elders, and hierarchy.",
            "special_occasions": ["Eid al-Fitr", "Eid al-Adha", "Independence Day (April 17)", "Ramadan"],
            "cultural_values": "Family, respect for tradition, hospitality, religion."
        },
        # Add more countries as needed...
    }

    # Default context if nationality is not found in the database
    return contexts.get(nationality, {
        "work_week": "Typically Sunday to Thursday or Monday to Friday, but may vary.",
        "communication_style": "Varies by individual and specific cultural context.",
        "special_occasions": "Varies by country and region.",
        "cultural_values": "Diverse cultural norms and practices depending on local and regional influences."
    })
