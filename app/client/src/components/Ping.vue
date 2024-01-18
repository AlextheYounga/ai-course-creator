<template>
    <div>
        <p>{{ msg }}</p>
    </div>
</template>
  
<script lang="ts">
import flaskApi from '@/router/api'

export default {
  name: 'Ping',
  data() {
    return {
      msg: '',
    };
  },
  methods: {
    getMessage() {
      flaskApi.get('/ping-pong').then((data) => {
        this.msg = data;
      });
    },
  },
  created() {
    this.getMessage();
  },
};
</script>