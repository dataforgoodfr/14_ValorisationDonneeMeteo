import type { GeometryCollection, Topology } from "topojson-specification";

export interface FranceDepartmentProperties {
    code: string;
}

export type FranceTopology = Topology<{
    DEP: GeometryCollection<FranceDepartmentProperties>;
    REG: GeometryCollection<FranceDepartmentProperties>;
}>;
