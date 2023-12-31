#https://github.com/dB-SPL/cot-types/blob/main/CoTtypes.xml
# Work needed to improve re-use

import uuid
import xml.etree.ElementTree as et
from time import time,gmtime,strftime
import datetime
import difflib

version = '4.9.0'

def cot_xml_to_dict(file_path):
    tree = et.parse(file_path)
    root = tree.getroot()
    xml_dict = {child.attrib['desc']: child.attrib.get('cot', None) for child in root if 'desc' in child.attrib and 'cot' in child.attrib}
    return xml_dict

def search_dict(xml_dict, search_string):
    search_string = search_string.upper()
    matches = difflib.get_close_matches(search_string, xml_dict.keys(), n=1, cutoff=0.0)
    if matches:
        closest_match = matches[0]
        return xml_dict.get(closest_match, "Not Found")
    else:
        return "Not Found"

# File path
file_path = "cot_types.xml"

# Convert COT XML to dictionary
xml_dict = cot_xml_to_dict(file_path)

ID = {
    "pending": "p",
    "unknown": "u",
    "assumed-friend": "a",
    "friend": "f",
    "neutral": "n",
    "suspect": "s",
    "hostile": "h",
    "joker": "j",
    "faker": "f",
    "none": "o",
    "other": "x"
}

datetime_strfmt = "%Y-%m-%dT%H:%M:%SZ"

def mkcot(my_uid, latitude, longitude, speed, course, cot_identity, cot_dimension, team_name, cot_callsign, sender_uid, tgt_call, tgt_uid, tgt_msg, stale, source):

    cot_stale = stale
    cot_how = "m" #Note that this could also be managed via cot_types.xml
    cot_lat = latitude
    cot_lon = longitude
    cot_hae = 9999999.0
    cot_ce = 9999999.0
    cot_le = 9999999.0
    cot_type = "a" # a for atom, an actual event/thing. t used for pings, etc
    cot_typesuffix = "" 
    cot_id = str(my_uid) # used to id a single CoT, could be sender UID, or event
    cot_ping = False
    cot_point = False
    cot_os = "1"   # Does not seem to matter, but is required for some CoT's
    cot_platform = source
    cot_version = version
    iconpath = None
    color = ""
    team_role = ""

    cot_dimension = search_dict(xml_dict, cot_dimension)
    
    # Get the current time and convert to CoT XML
    now_xml = strftime(datetime_strfmt,gmtime())
    #now_xml = str(datetime.datetime.now())

    # Add the stale time to the current time and convert to CoT XML
    stale = gmtime(time() + (60 * cot_stale))
    stale_xml = strftime(datetime_strfmt,stale)

    # If cot is a ping append "-ping" to UID
    if cot_ping:
        cot_id = cot_id + "-ping"

    if cot_identity:
        unit_id = ID[cot_identity]
        if cot_dimension:
            cot_typestr = cot_dimension.replace(".",unit_id)
    else:
        cot_typestr = cot_type # No unit, just go with basic type

    if cot_typesuffix:     
        # append the type suffix to the type string
        cot_typestr = cot_typestr + "-" + cot_typesuffix

    if not tgt_call:
        event_attr = {
            "version": "2.0",
            "uid": cot_id, # uid of the CoT, sender or event 
            "time": now_xml,
            "start": now_xml,
            "stale": stale_xml,
            "how": cot_how, 
            "type": cot_typestr
        }

    else:
        event_attr = {
            "version": "2.0",
            "uid": "GeoChat." + my_uid + "." + tgt_call + "." + str(uuid.uuid1()), # uid of the CoT, sender or event 
            "time": now_xml,
            "start": now_xml,
            "stale": stale_xml,
            "how": "cot_how", 
            "type": "b-t-f"
        }

    point_attr = {
        "lat": str(cot_lat),
        "lon":  str(cot_lon),
        "hae": str(cot_hae),
        "ce": str(cot_ce),
        "le": str(cot_le)
    }

    # now the sub-elements for the detail block
    if not tgt_call:
        precision_attr = {
            "altsrc": "GPS",
            "geopointsrc": "GPS",
        }
        track = {
            "speed": str(speed), 
            "course": str(course),
        }

    else:
        precision_attr = None

    # if not a geochat we always have to include the contact block
    if not tgt_call and not cot_point:
        if cot_callsign:
            contact_attr = {
                "endpoint": "*:-1:stcp",
                "callsign": cot_callsign
            }
        else:
            contact_attr = { } # still have to include the block
            team_name = "" # No need for team if no callsign
    else:
        contact_attr = None
    

    if team_name and not tgt_call:
        # only use if the team is defined and it's not a geochat
        group_attr = {  
            "role": team_role,
            "name": team_name
        }
    else:
        group_attr = None
        

    if not tgt_call:
        platform_attr = {
            "os": cot_os, 
            "platform": cot_platform, 
            "version": cot_version
        }
    else:
        platform_attr = None


    if iconpath is None:
        icon_attr = None

    else:
        icon_attr = {
            "iconsetpath": iconpath     # Can specify path to custom icons eg "iconsetpath": 'f7f71666-8b28-4b57-9fbb-e38e61d33b79/Google/placemark_circle.png'
        }

    if color:
        color_attr = { "argb": '-8454017' }
    else:
        color_attr = None

    # Geochat Attributes -----------------------------------------------

    chat_attr = {
        "chatroom": tgt_call,
        "id": sender_uid,
        "senderCallsign": cot_callsign
    }

    chatgrp_attr = {
        "uid0": sender_uid,
        "uid1": tgt_uid,
        "id": tgt_uid
    }

    link_attr = {
        "uid": sender_uid,
        "type": cot_typestr,
        "relation": "p-p"
    }

    remarks_attr = { # actual text is appended later as a "tail"
        #"source": "TAKPAK." + sender_uid,  # works, but shows as a different user, same call
        #"source": "BAO.F.ATAK." + sender_uid, # the magic prefix are critical to spoof a user
        "source": sender_uid,
        "to": tgt_uid,
        "time": now_xml,
    }

    martidest_attr = {
        "callsign": tgt_call,
    }

    # Now assemble the element tree
    cot = et.Element('event', attrib=event_attr)

    et.SubElement(cot,'point', attrib=point_attr)

    # Create Detail element, save the handle
    detail = et.SubElement(cot, 'detail')

    # Now add some subelements to detail
    # Geochat has different required elements
    if tgt_call:  # target_call means a geochat
        chat = et.SubElement(detail,'__chat', attrib=chat_attr)
        et.SubElement(chat,'chatgrp', attrib=chatgrp_attr)
        et.SubElement(detail,'link', attrib=link_attr)

        # remarks block required
        remarks = et.SubElement(detail,'remarks', attrib=remarks_attr)
        remarks.text= tgt_msg # This is the actual message

        # serverdestination req'd
        #et.SubElement(detail,'__serverdestination', attrib=serverdestination)

        #marti=et.SubElement(detail,'marti', attrib=marti_attr)
        marti=et.SubElement(detail,'marti')
        et.SubElement(marti,'dest', attrib=martidest_attr)


    if not cot_ping:
        # Add the contact block, needed except for pings
        if contact_attr:
            et.SubElement(detail,'contact', attrib=contact_attr)

        if precision_attr:
            et.SubElement(detail,'precisionlocation', attrib=precision_attr)
            et.SubElement(detail,'track', attrib=track)

        if group_attr: # Don't include the block if set to "" as override
            et.SubElement(detail,'__group', attrib=group_attr)

        # takv/platform stuff needed for PLI's
        if platform_attr:
            et.SubElement(detail,'takv', attrib=platform_attr)

        # Optional icon/color
        if icon_attr is not None:
            et.SubElement(detail,'usericon', attrib=icon_attr)
        if color_attr:
            et.SubElement(detail,'color', attrib=color_attr)


    # Prepend the XML header
    cot_xml = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + b'\n' + et.tostring(cot)
    return cot_xml.decode()