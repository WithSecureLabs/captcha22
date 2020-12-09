<!-- components/Login.vue -->
<template>
  <b-container fluid>
    <div class="form-wrapper">
         <p class="subtitle error-msg">{{ errorMsg }}</p>
      <b-form @submit.prevent="">
        <b-form-group
          :label-cols="3"
          breakpoint="md"
          horizontal
          label="Captcha Title:"          
          for="captchatitle">
          <b-col :md="10">
            <b-input
              id="captchatitle"
              :state="Boolean(captchatitle)"
              v-model="captchatitle"
              maxlength="100"
              required />
          </b-col>
        </b-form-group>
        <b-form-group
          :label-cols="3"
          breakpoint="md"
          horizontal
          label="Select File:"
          for="filename">
          <b-col :md="10">
          <b-form-file
            id="filename"
            v-model="file1"
            :state="Boolean(file1)"
            placeholder="Choose a zip or drop it here..."
            drop-placeholder="Drop file here..."
           @change="handleFileChange"></b-form-file>
           </b-col>
          </b-form-group>
        <b-col
          :md="5"
          offset="4">
          <b-button
            type="submit"
            variant="success" @click="register">Submit</b-button>               
        </b-col>
      </b-form>
    </div>
  </b-container>
</template>

<script>

export default {
  name: 'Register',
  data () {
      return {
          captchatitle: '',
          captchazip: '', 
          value: File,         
          errorMsg: '',
          file1 : null
      }
  },
  methods: {   
      created() {
          console.log("Testing the level of access:" + this.$store.getters.isAuthenticated);
      },  
      register() {
        console.log("Test got to here");
        this.errorMsg = '';
        console.log("Testing the level of acces:" + this.$store.getters.isAuthenticated);
        console.log(this.captchazip);

        this.$store.dispatch("uploadCaptcha", { name: this.captchatitle, contents: this.captchazip }).then(response => { 
            console.log(response.data);         
            //Navigate user to this new captcha
            this.$router.push({ name: 'CaptchaDetails', params: {id: response.data.captcha.uri.split("/")[response.data.captcha.uri.split("/").length - 1]}});
          });



        //this.$store.dispatch('register', {username: this.username, password: this.password, firstname: this.firstname, surname: this.surname}).then(() => {if (this.errorMsg == '') {this.$router.push('/login')}});
      },
      handleFileChange(e) {
      // Whenever the file changes, emit the 'input' event with the file data.     
      this.captchazip = e.target.files[0];
      //this.$emit('input', e.target.files[0])
    }
  },
  mounted () {
      //EventBus.$on('failedRegister', (msg) => {
      //    this.errorMsg = msg;
      //})
  },
  beforeDestroy () {
      //EventBus.$off('failedRegister');
  }  
};
</script>