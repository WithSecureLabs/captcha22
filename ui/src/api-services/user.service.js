import Axios from 'axios';

const RESOURCE_NAME = '/user';

export default {
    getAll(jwt) {
        return Axios.get(RESOURCE_NAME, {
            headers: {
                Authorization: `Bearer ${jwt}`
            }
        });
    },

    getUser(data, jwt) {
        return Axios.get(RESOURCE_NAME, {
            headers: {
                Authorization: `Bearer ${jwt}`
            },
            params: {
                username: data.id
            }
        });
    },

    deleteUser(data, jwt) {
        return Axios.delete(RESOURCE_NAME, {
            headers: {
                Authorization: `Bearer ${jwt}`
            },
            params: {
                username: data.username
            }
        })
    },

    updateUser(data, jwt) {
        console.log(data);
        return Axios.put(RESOURCE_NAME, {
            Username: data.user.username,
            FirstName: data.user.firstname,
            Surname: data.user.surname,
            Role: data.user.role,
            PicFilename: data.user.picFilename
        }, {
            headers: {
                Authorization: `Bearer ${jwt}`
            },
            params: {
                username: data.id
            },
        });
    },

    uploadPic(data, jwt) {
        var formData = new FormData();
        formData.append("file", data.file)
        return Axios.post('/UploadProfilePic', formData, {
            headers: {
                Authorization: `Bearer ${jwt}`
            }
        });
    }
}