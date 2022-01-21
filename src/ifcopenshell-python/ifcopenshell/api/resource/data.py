# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import ifcopenshell
import ifcopenshell.util.date
from ifcopenshell.api.cost.data import CostValueTrait


class Data(CostValueTrait):
    is_loaded = False
    resources = {}
    resource_times = {}
    cost_values = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.resources = {}
        cls.resource_times = {}
        cls.cost_values = {}

    @classmethod
    def load(cls, file):
        cls._file = file
        if not cls._file:
            return
        cls.load_resources()
        cls.load_resource_times()
        cls.is_loaded = True

    @classmethod
    def load_resources(cls):
        cls.resources = {}
        cls.cost_values = {}
        for resource in cls._file.by_type("IfcResource"):
            data = resource.get_info()
            del data["OwnerHistory"]
            data["IsNestedBy"] = []
            for rel in resource.IsNestedBy:
                [data["IsNestedBy"].append(o.id()) for o in rel.RelatedObjects]
            data["Nests"] = []
            for rel in resource.Nests:
                [data["Nests"].append(rel.RelatingObject.id())]
            data["ResourceOf"] = []
            for rel in resource.ResourceOf:
                [data["ResourceOf"].append(o.id()) for o in rel.RelatedObjects]
            data["HasContext"] = resource.HasContext[0].RelatingContext.id() if resource.HasContext else None
            if resource.Usage:
                data["Usage"] = data["Usage"].id()
            data["TotalCostQuantity"] = cls.get_total_quantity(resource)
            if resource.BaseQuantity:
                data["BaseQuantity"] = resource.BaseQuantity.get_info()
                del data["BaseQuantity"]["Unit"]
            if resource.BaseCosts:
                data["BaseCosts"] = [e.id() for e in resource.BaseCosts]
                cls.load_cost_values(resource, data)
            cls.resources[resource.id()] = data

    @classmethod
    def load_resource_times(cls):
        cls.resource_times = {}
        for resource_time in cls._file.by_type("IfcResourceTime"):
            data = resource_time.get_info()
            for key, value in data.items():
                if not value:
                    continue
                if "Start" in key or "Finish" in key or key == "StatusTime":
                    data[key] = ifcopenshell.util.date.ifc2datetime(value)
                elif "Work" in key or key == "LevelingDelay":
                    data[key] = ifcopenshell.util.date.ifc2datetime(value)
            cls.resource_times[resource_time.id()] = data
