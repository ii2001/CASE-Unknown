export type Suspect = { id:string; name:string; role:string; public_profile:string; portrait_url:string }
export type Location = { id:string; name:string; description:string; locked:boolean; image_url:string }
export type Evidence = { id:string; title:string; category:string; critical:boolean; description:string; image_url:string|null }
export type Solution = { culprit_id:string; motive:string; crime_time:string; crime_method:string; timeline:string[]; summary:string; missed_clues:string[] }
export type Game = { id:string; title:string; genre:string; introduction:string; incident_summary:string; current_location_id:string; visited_location_ids:string[]; unlocked_location_ids:string[]; narratives:string[]; completed:boolean; won:boolean|null; suspects:Suspect[]; locations:Location[]; evidence:Evidence[]; interviews:{suspect_id:string;question:string;answer:string}[]; cover_url:string; solution?:Solution }
