# shipBonusSupercarrierG3WarpStrength
#
# Used by:
# Ship: Nyx
type = "passive"
def handler(fit, src, context):
    fit.ship.increaseItemAttr("warpScrambleStatus", src.getModifiedItemAttr("shipBonusSupercarrierG3"), skill="Gallente Carrier")
