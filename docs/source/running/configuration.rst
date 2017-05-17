.. Title

Configuration
=============
One of the goals of this project is to make configuring and running ECRF/LVF simpler.  One of the
ways that can be accomplished is by having common sense default values for most things and only
requiring changes for things that are truly specific for a customer or environment.

To that end, the configuration system of ECRF and LVF relies on two different configuration files.
One that contains the default or standard settings that will be the same across all environments,
and another that contains those settings that are custom.  We should be able to set most things
in the default config and have them stay static for most (if not all) deployments.  If there is
a need to provide an alternate value for a default setting, it can be overridden with a custom
setting in the custom configuration file.

The configuration system consists, then, of two files:
1) lostconfig.ini - contains the customizable, environment specific settings that can be changed, e.g.
database connection strings, customer or service-specific routing behaviors, etc.
2) lostconfig.default.ini - contains the static defaults that will remain the same across all environments, e.g. service
URN to UDM feature-class table mappings, DNS resolver settings, location validation settings, etc.



