import api from "./api";

export async function getConversations() {

    const response = await api.get("/auth/conversations");

    return response.data;

}

export async function getConversation(id) {

    const response = await api.get(

        `/auth/conversation/${id}`

    );

    return response.data;

}
export async function deleteConversation(id) {

    const response = await api.delete(

        `/conversation/${id}`

    );

    return response.data;

}
export async function renameConversation(id, title) {

    const response = await api.put(

        `/conversation/${id}`,

        {
            title
        }

    );

    return response.data;

}