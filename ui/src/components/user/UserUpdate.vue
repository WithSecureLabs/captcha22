<template>
  <div>
    <div class="well">
      <br />
      <form v-on:submit.prevent="onSubmit">
        <div class="row">
          <div class="col-md-3">
            <label for="firstname">
              <strong>First Name:</strong>
            </label>
          </div>
          <div class="col-md-3">
            <input v-model="user.firstname" type="text" id="firstname" />
          </div>
        </div>
        <div class="row">
          <div class="col-md-3">
            <label for="surname">
              <strong>Surname:</strong>
            </label>
          </div>
          <div class="col-md-3">
            <input v-model="user.surname" type="text" id="surname" />
          </div>
        </div>
        <div class="row">
          <div class="col-md-3">
            <label for="username">
              <strong>Username:</strong>
            </label>
          </div>
          <div class="col-md-3">
            <input v-model="user.username" type="text" id="surname" />
          </div>
        </div>
        <div class="row">
          <div class="col-md-3">
            <label for="profilepic">
              <strong>Profile Pic Upload</strong>
            </label>
          </div>
          <div class="col-md-3">
            <input type="file" id="profilepic" @change="processFile($event)" />
          </div>
        </div>Note: File must be ".jpg", ".jpeg", ".png", or ".gif".
        <div class="row">
          <div class="col-md-3">
            <input type="submit" value="Submit" />
          </div>
        </div>
      </form>
    </div>
  </div>
</template>
<script>
import UserService from "@/api-services/user.service";

export default {
  name: "UserUpdate",
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
        console.log(this.user);
      });
  },
  methods: {
    processFile(event) {
      this.picFile = event.target.files[0];
    },
    onSubmit() {
      if (this.picFile != undefined) {
        this.$store
          .dispatch("uploadPic", { file: this.picFile })
          .then(() => {
            this.user.picFilename = this.picFile.name;
            this.$store
              .dispatch("updateUser", {
                id: this.$router.currentRoute.params.id,
                user: this.user
              })
              .then(response => {
                this.$router.push({ name: "UserList" });
              })
              .catch(() => {
                alert("Could not update user. Unknown error.");
              });
          })
          .catch(error => {
            alert(
              "Failed to upload image. Make sure the file type is correct."
            );
          });
      } else {
        this.$store
          .dispatch("updateUser", {
            id: this.$router.currentRoute.params.id,
            user: this.user
          })
          .then(response => {
            this.$router.push({ name: "UserList" });
          })
          .catch(() => {
            alert("Could not update user. Unknown error.");
          });
      }
    }
  }
};
</script>