import api from "./api";

export async function indexGithub(repoUrl) {

    const response = await api.post("/github/index", {

        repo_url: repoUrl

    });

    return response.data;

}