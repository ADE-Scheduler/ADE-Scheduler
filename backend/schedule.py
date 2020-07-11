"""
Schedule data format:
{
    code_list: [LMECA2660, LELEC2760, etc],             // requested course codes
    filtered_subcodes: [LELEC2760_Q1, LMECA2660_Q2],    // unselected subcodes
    computed_subcode: [[code1, code2], ..., [code2, code4]]   // filtered subcodes, week by week
    custom_events: [{event1}, {event2}],                // custom user events
    priority_levels: {code1: 5, code2: 1, subcode1: 3}, // priority level of the various code & subcodes
    project_id: id,
    schedule_id: id,
}
"""
