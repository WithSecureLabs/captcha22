<!-- components/Login.vue -->
<template>
  <b-container fluid>
    <div class="form-wrapper">
         <p class="subtitle error-msg">{{ errorMsg }}</p>
      <b-form @submit.prevent="">
        <b-form-group
          :label-cols="2"
          breakpoint="md"
          horizontal
          label="Username:"
          for="username">
          <b-col :md="5">
            <b-input
              id="username"
              v-model="username"
              maxlength="60"
              required />
          </b-col>
        </b-form-group>

        <b-form-group
          :label-cols="2"
          breakpoint="md"
          horizontal
          label="Password:"
          for="pasword">
          <b-col :md="5">
            <b-input
              id="password"
              v-model="password"
              type="password"
              required />
          </b-col>
        </b-form-group>        
        
        <br >

        <b-col
          :md="5"
          offset="4">
          <b-button
            type="submit"
            variant="success" @click="register">Login</b-button>
          <b-button            
            variant="danger" @click="register">Cancel</b-button>             
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
          username: '',
          password: '',
          errorMsg: ''
      }
  },
  methods: {   
      created() {
          console.log("Testing the level of access:" + this.$store.getters.isAuthenticated);
      },  
      register() {  
        console.log("In the register function");      
        this.errorMsg = '';        
        console.log("Error set to zero");
        this.$store.dispatch('register', {username: this.username, password: this.password}).then(() => {if (this.errorMsg == '') {this.$router.push('/login')}});
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