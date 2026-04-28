export type DeviationStationIdAndName = {
    station_id: string;
    station_name: string;
};

export interface InfoParagraph {
    title?: string;
    text: string;
}

export interface InfoSection {
    label: string;
    content: string | InfoParagraph[];
}
