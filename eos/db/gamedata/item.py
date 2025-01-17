# ===============================================================================
# Copyright (C) 2010 Diego Duclos
#
# This file is part of eos.
#
# eos is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# eos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with eos.  If not, see <http://www.gnu.org/licenses/>.
# ===============================================================================

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Table
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import backref, deferred, mapper, relation, synonym
from sqlalchemy.orm.collections import attribute_mapped_collection

from eos.db import gamedata_meta
from eos.db.gamedata.dynamicAttributes import dynamicApplicable_table
from eos.db.gamedata.effect import typeeffects_table
from eos.gamedata import Attribute, DynamicItem, Effect, Group, Item, Traits, MetaGroup

items_table = Table("invtypes", gamedata_meta,
                    Column("typeID", Integer, primary_key=True),
                    Column("typeName", String, index=True),
                    Column("description", String),
                    Column("raceID", Integer),
                    Column("factionID", Integer),
                    Column("volume", Float),
                    Column("mass", Float),
                    Column("capacity", Float),
                    Column("published", Boolean),
                    Column("marketGroupID", Integer, ForeignKey("invmarketgroups.marketGroupID")),
                    Column("iconID", Integer),
                    Column("graphicID", Integer),
                    Column("groupID", Integer, ForeignKey("invgroups.groupID"), index=True),
                    Column("metaLevel", Integer),
                    Column("metaGroupID", Integer, ForeignKey("invmetagroups.metaGroupID"), index=True),
                    Column("variationParentTypeID", Integer, ForeignKey("invtypes.typeID"), index=True),
                    Column("replacements", String))

from .traits import traits_table  # noqa

mapper(Item, items_table,
       properties={
           "group"            : relation(Group, backref=backref("items", cascade="all,delete")),
           "_Item__attributes": relation(Attribute, cascade='all, delete, delete-orphan', collection_class=attribute_mapped_collection('name')),
           "effects": relation(Effect, secondary=typeeffects_table, collection_class=attribute_mapped_collection('name')),
           "metaGroup"        : relation(MetaGroup, backref=backref("items", cascade="all,delete")),
           "varParent"        : relation(Item, backref=backref("varChildren", cascade="all,delete"), remote_side=items_table.c.typeID),
           "ID"               : synonym("typeID"),
           "name"             : synonym("typeName"),
           "description"      : deferred(items_table.c.description),
           "traits"           : relation(Traits,
                                         primaryjoin=traits_table.c.typeID == items_table.c.typeID,
                                         uselist=False),
           "mutaplasmids": relation(DynamicItem,
                   primaryjoin=dynamicApplicable_table.c.applicableTypeID == items_table.c.typeID,
                   secondaryjoin=dynamicApplicable_table.c.typeID == DynamicItem.typeID,
                   secondary=dynamicApplicable_table,
                   backref="applicableItems")})

Item.category = association_proxy("group", "category")
