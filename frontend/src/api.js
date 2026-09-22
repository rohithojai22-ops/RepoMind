import axios from "axios";
export const api=axios.create({baseURL:import.meta.env.VITE_API_URL||"http://localhost:8000/api"});
export async function ingestRepository(url){return (await api.post("/repositories",{url})).data}
export async function getRepositories(){return (await api.get("/repositories")).data}
export async function askQuestion(repository_id,question){return (await api.post("/chat",{repository_id,question})).data}
