.. _civvy-map:

****************************************
Mapping fields for Civic Address Queries
****************************************

For civvy, we need a``civvy_map`` to tell civvy which fields match up with which CLDXF elements when executing a civic address search.
Below you will see the default we have set for ``civvy_map`` in configuration. Please use caution when editing this, and only make edits if you're sure you need them.
Here is our default for civvy_map:

.. code-block:: python

    """
        {
            "streets" : {
                "extras" : {
                    "schema" : "active"
                },
                "collection" : "roadcenterline",
                "geometry" : "wkb_geometry",
                "ref_id" : "gcunqid",
                "label" : ["countyl", "countyr", "predir", "pretype", "strname", "posttype", "postdir"],
                "properties" : {
                    "country" : ["countryl", "countryr"],
                    "a1" : ["statel", "stater"],
                    "a2" : ["countyl", "countyr"],
                    "a3" : ["incmunil", "incmunir", "uninccomml", "uninccommr"],
                    "a6" : "strname",
                    "rd" : "strname",
                    "prd" : "predir",
                    "pod" : "postdir",
                    "sts" : "posttype",
                    "hno" : ["fromaddl", "toaddl", "fromaddr", "toaddr"],
                    "pc" : ["zipcodel", "zipcoder"],
                    "pcn": ["postcomml", "postcommr"],
                    "stp": "pretype",
                    "stps": "pretypesep",
                    "prm": "premod"
                },
                "sides" : {
                    "left" : [
                        "statel", "countyl", "incmunil", "uninccomml", "fromaddl", "toaddl", "zipcodel"
                    ],
                    "right" : [
                        "stater", "countyr" , "incmunir", "uninccomml", "fromaddr", "toaddr", "zipcoder"
                    ]
                },
                "ranges" : {
                    "bottom" : [ "fromaddl", "fromaddr" ],
                    "top" : [ "toaddl", "toaddr" ]
                }
            },
            "points" : {
                "extras" : {
                    "schema" : "active"
                },
                "collection" : "ssap",
                "geometry" : "wkb_geometry",
                "ref_id" : "gcunqid",
                "label" : ["county", "addnum", "predir", "pretype", "strname", "posttype", "postdir"],
                "properties" : {
                    "country" : "country",
                    "a1" : "state",
                    "a2" : "county",
                    "a3" : ["incmuni", "uninccomm"],
                    "a6" : "strname",
                    "rd" : "strname",
                    "prd" : "predir",
                    "pod" : "postdir",
                    "sts" : "posttype",
                    "hno" : "addnum",
                    "hns" : "addnumsuf",
                    "lmk" : "landmark",
                    "pc" : "zipcode",
                    "loc": "location",
                    "flr": "floor",
                    "stp": "pretype",
                    "stps": "pretypesep",
                    "unit": "unit",
                    "pcn": "postcomm",
                    "prm": "premod",
                    "mp": "milepost",
                    "bld": "building",
                    "room": "room",
                    "seat": "seat",
                    "plc": "placetype"
                },
                "appendix" : "adddatauri"
            }
        }
        """

Key Areas of the Mapping:
^^^^^^^^^^^^^^^^^^^^^^^^^

+---------------------+----------------+-----------------------------------------------------------------------------------------------+
| Key                 | Sample         | Description                                                                                   |
+=====================+================+===============================================================================================+
| civvy designation   | streets        | Name of the collection for these search parameters. Available Names: streets, points.         |
+---------------------+----------------+-----------------------------------------------------------------------------------------------+
| extras.schema       | active         | A data store may contain more than one schema, this points it to the correct one.             |
+---------------------+----------------+-----------------------------------------------------------------------------------------------+
| collection          | ssap           | Which feature class we want to search on.                                                     |
+---------------------+----------------+-----------------------------------------------------------------------------------------------+
| geometry            | wkb_geometry   | Where, within the features, the geometry is stored.                                           |
+---------------------+----------------+-----------------------------------------------------------------------------------------------+
| ref_id              | UUID           | Unique Identifier in the feature class.                                                       |
+---------------------+----------------+-----------------------------------------------------------------------------------------------+
| label               | See above.     | A collection of fields used to write the label to be a part of the search result.             |
+---------------------+----------------+-----------------------------------------------------------------------------------------------+
| properties          | See above.     | Key: CLDXF Element Value: field name to search within the feature class                       |
+---------------------+----------------+-----------------------------------------------------------------------------------------------+
| appendix            | adddatauri     | Any extra data you may want from the features. (Not used in searching)                        |
+---------------------+----------------+-----------------------------------------------------------------------------------------------+
| sides               | See above      | For streets, we have a left and right side for some values. All must be mapped                |
+---------------------+----------------+-----------------------------------------------------------------------------------------------+
| ranges              | See above      | We have road ranges for address numbers, these must be mapped for valid and accurate results. |
+---------------------+----------------+-----------------------------------------------------------------------------------------------+


