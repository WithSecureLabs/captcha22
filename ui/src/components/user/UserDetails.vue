<template>
  <div>
    <div class="well">
      <div class="row">
        <div class="col-md-3">
          <strong>Profile Pic:</strong>
        </div>
        <div class="col-md-3">
          <img id="profilepicimg" />
        </div>
      </div>
      <div class="row">
        <div class="col-md-3">
          <strong>Name:</strong>
        </div>
        <div class="col-md-3">{{ user.firstname + ' ' + user.surname }}</div>
      </div>
      <div class="row">
        <div class="col-md-3">
          <strong>Username:</strong>
        </div>
        <div class="col-md-3">{{ user.username }}</div>
      </div>
      <div v-if="user.role == 0" class="row">
        <div class="col-md-3">
          <strong>Type of user:</strong>
        </div>
        <div class="col-md-3">
          <span class="text-success">Student</span>
        </div>
      </div>
      <div v-else class="row">
        <div class="col-md-3">
          <strong>Type of user:</strong>
        </div>
        <div class="col-md-3">
          <span class="text-info">Lecturer</span>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import UserService from "@/api-services/user.service";

export default {
  name: "UserDetails",
  data() {
    return {
      user: {}
    };
  },
  created() {
    this.$store
      .dispatch("getUser", { id: this.$router.currentRoute.params.id })
      .then(response => {
        this.user = response.data;
        document.querySelector("#profilepicimg").src = `http://localhost:8000/API/GetProfilePic?filename=${this.user.picFilename}`;
      });
  }
};
</script>