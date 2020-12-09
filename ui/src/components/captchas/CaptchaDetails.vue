<template>
    <div> 
      <b-container class="main-container">
      <b-row>
        <b-col><h2>General Information</h2></b-col>
      </b-row>
      <b-row>
        <b-col><h3><strong>Title:</strong> {{captcha.title}} </h3></b-col>
        
        <b-col><h3><strong>Model Number: </strong> {{captcha.modelNumber}}</h3></b-col>
      </b-row>
      <br/>

      <b-row>
        <b-col><strong>Model Trained: </strong> 
          <div v-if="captcha.busyTraining">
            <b-icon icon="circle-fill" animation="fade" font-scale="3" variant="warning"></b-icon>
          </div>
          <div v-else>  
            <b-icon icon="check-circle-fill" font-scale="3" variant="success"></b-icon>
          </div>
        </b-col>

        <b-col><strong>Model Stored: </strong> 
          <div v-if="captcha.hasModel">
            <b-icon icon="check-circle-fill" font-scale="3" variant="success"></b-icon>                  
          </div>
          <div v-else>
            <b-icon icon="x-circle-fill" font-scale="3" variant="danger"></b-icon>                  
          </div>
                
        </b-col>
        <b-col><strong>Model Active: </strong> 
          <div v-if="captcha.modelActive">
            <b-icon icon="check-circle-fill" animation="fade" font-scale="3" variant="success"></b-icon>
          </div> 
          <div v-else>
            <b-icon icon="x-circle-fill" font-scale="3" variant="danger"></b-icon>                  
          </div>
        </b-col>
      </b-row>

      <br/>

      <b-row>
        <b-col></b-col>                     
        <b-col> <b-button variant="outline-primary" @click="onDownloadModelClick">Download</b-button> </b-col> 
        <b-col v-if="captcha.modelActive"> <b-button variant="outline-danger" @click="onDeactivateModelClick">Deactivate</b-button> </b-col> 
        <b-col v-else> <b-button variant="outline-success" @click="onActivateModelClick">Activate</b-button> </b-col> 
      </b-row>

      <br/><br/>



      <b-row>
        <b-col><h2>Training Information</h2></b-col>
      </b-row>

      <b-row>
        <b-col v-if="captcha.busyTraining"><strong>Current Training Step: </strong>{{training_info.last_step}} </b-col>
        <b-col v-else><strong>Training Completed</strong></b-col>
        <b-col><strong>Checkpoint Step: </strong>{{training_info.checkpoint}}</b-col>
        <b-col><strong>Last Step: </strong>{{training_info.last_step}}</b-col>
      </b-row>

      <br/>

      <b-row>
        <b-col><strong>Loss:</strong> {{training_info.loss}}</b-col>
        <b-col><strong>Perplexity</strong> {{training_info.perplexity}}</b-col>
      </b-row>

      <br/><br/>

      <b-row>
        <b-col><h2>Results</h2></b-col>
      </b-row>

      <br/>

      <b-row>
        <b-col>
            <span>Correct: <strong>{{ results_info.correct }} / {{ results_info.totalPredictions }}</strong></span>
          <b-progress :max="results_info.totalPredictions" height="2rem">
            <b-progress-bar :variant="getVariantType(results_info.correct / results_info.totalPredictions * 100)"  :value="results_info.correct ">
              
            </b-progress-bar>
          </b-progress>
        </b-col>
      </b-row>

      <br/>

      <b-row>
        <b-col>
          <div class="accordion" role="tablist">
            <b-card no-body class="mb-1">
              <b-card-header header-tag="header" class="p-1" role="tab">
                <b-button block v-b-toggle.accordion-1 variant="dark">Wrong Answers</b-button>
              </b-card-header>
              <b-collapse id="accordion-1" accordion="my-accordion" role="tabpanel">
                <b-card-body>
                  <b-list-group>
                    <b-list-group-item v-for="answer in wrong_answers" :key="answer">
                    {{ answer }}
                    </b-list-group-item>
                </b-list-group>                  
                </b-card-body>
              </b-collapse>
            </b-card>
          </div>          
        </b-col>
      </b-row>
    </b-container>  
    
    
  </div>
</template>
<script>
import CaptchaService from "@/api-services/captchas.service";

export default {
  name: "CaptchaDetails",
  data() {
    return {
      captcha: {},
      training_info: {},
      results_info: {},
      wrong_answers: null,
    };
  },
  methods: {  
    getVariantType: function(correct) {     
      if (correct > 80) {
        return 'success'
      } else if (correct > 60) {
        return 'warning'
      } else if (correct > 50) {
        return 'danger'
      } else if (correct > 30) {
        return 'secondary'
      }
      return 'dark'
    },    
    
    onCaptchaClick() {
      console.log('captcha', this.captcha.uri);
     // this.$router.push({ name: 'UserUpdate', params: {id: username}});

     //The important part in this entry
    },
    onActivateModelClick() {
      console.log("Going to activate the model");

      this.$store.dispatch("activateCaptchaModel", { id: this.captcha.dataToken, answer: true }).then(response => { 
            console.log(response.data);         
            //this.training_info = response.data.update;
          });
    },

    onDeactivateModelClick() {
      console.log("Going to de-activate the model");

      this.$store.dispatch("activateCaptchaModel", { id: this.captcha.dataToken, answer: false }).then(response => { 
            console.log(response.data);         
            //this.training_info = response.data.update;
          });
    },

    onDownloadModelClick() {
      console.log("Going to download the model");

      this.$store.dispatch("downloadCaptchaModel", { id: this.captcha.dataToken }).then(response => { 
                  
            var fileURL = window.URL.createObjectURL(new Blob([response.data]));
            var fileLink = document.createElement('a');
            fileLink.href = fileURL;
            fileLink.setAttribute('download', 'exported-model.zip');
            document.body.appendChild(fileLink);
            fileLink.click();
          });
    },
    

  },
  computed: {
    isAuthenticated () {      
      return this.$store.getters.isAuthenticated;
    },      
  },
  created() {
    this.$store
      .dispatch("getCaptcha", { id: this.$router.currentRoute.params.id })
      .then(response => {
          console.log('details', response.data);
        this.captcha = response.data.captcha;        

        this.$store.dispatch("getCaptchaTraining", { id: this.captcha.dataToken }).then(response => { 
            console.log(response.data);         
            this.training_info = response.data.update;
          });

        this.$store.dispatch("getCaptchaResults", { id: this.captcha.dataToken }).then(response => {          
            console.log(response.data);
            this.results_info = response.data.results;

            var formatted = this.results_info.wrong_answers.replace(/'/g, '"');
            //formatted = "'" + formatted + "'";
            formatted = formatted.replaceAll(' (', '');
            formatted = formatted.replaceAll(') ', '');

            this.wrong_answers = JSON.parse(formatted.toString());
            console.log(this.wrong_answers);
          });



      });    
  }
};
</script>