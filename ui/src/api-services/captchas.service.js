import Axios from 'axios';

const RESOURCE_NAME = '/captchas';

const TRAINING_NAME = '/training_update';

const RESULTS_NAME = '/results'

const MODEL_ACTIVATE_NAME = '/activate_model';

const MODEL_EXPORT_NAME = '/export_model';

const UPLOAD_NAME = '/captchas';

export default {
    getAll(jwt) {
        return Axios.get(RESOURCE_NAME, { 
            headers: { 
                'X-Api-Key': jwt
            }
        });
    },

    getCaptcha(data, jwt) {
        return Axios.get(RESOURCE_NAME + "/" + data.id, {
            headers: { 
                'X-Api-Key': jwt
            }            
        });
    },

    getCaptchaTraining(data, jwt) {
        return Axios.get(TRAINING_NAME + "/" + data.id, {
            headers: { 
                'X-Api-Key': jwt
            }            
        });
    },

    getCaptchaResults(data, jwt) {
        return Axios.get(RESULTS_NAME + "/" + data.id, {
            headers: { 
                'X-Api-Key': jwt
            }            
        });
    },

    activateCaptchaModel(data, jwt) {
        var data = {
            active: data.answer,
            dataToken : data.id
        }
        console.log(data);
        return Axios.post(MODEL_ACTIVATE_NAME, data, {
            headers: { 
                'X-Api-Key': jwt
            },    
    });
    },

    downloadCaptchaModel(data, jwt) {
        return Axios.get(MODEL_EXPORT_NAME + "/" + data.id, {
            headers: { 
                'X-Api-Key': jwt
            }            
        });
    },

    uploadCaptcha(data, jwt) {
        var datastuff = {            
                title : data.name            
        }
        const formData = new FormData();

        var file1 = new Blob([
            JSON.stringify({title : data.name})
         ], { type: 'application/json' });

         var file2 = new Blob([
            data.contents
         ], { type: 'application/octet' });

         console.log(file1);
         console.log(file2);

        formData.append('document', file2);
        formData.append('captcha', file1)

        console.log(formData);
        return Axios.post(UPLOAD_NAME, formData, {
            headers: { 
                'X-Api-Key': jwt
            },    
    });
    },

    getFiltered(jwt, dStart, dEnd, category) {
        if (category == null)
        {
            category = 1;
        }
        return Axios.get(RESOURCE_NAME + "/filter", {
            headers: { 
                'X-Api-Key': jwt
            },
            params: {
                categoryID: category,
                dateStart : dStart,
                dateEnd : dEnd,
            }
        });
    },
}