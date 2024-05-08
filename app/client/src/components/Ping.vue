<template>
    <div class="container mx-auto max-w-3xl py-12">
      <div class="text-center">
        <h1 class="text-white text-3xl">{{ msg }}</h1>
        <h2 class="text-white text-2xl">{{ count }} topics in DB!</h2>
      </div>
    </div>
</template>
  
<script>
import fastApi from '@/router/api'

export default {
  name: 'Ping',
  data() {
    return {
      msg: '',
      count: 0
    };
  },
  methods: {
    getMessage() {
      fastApi.get('/ping').then((res) => {
        console.log(res)
        this.$data.msg = res.data.message;
        this.$data.count = res.data.topics_count;
      });
    },
  },
  created() {
    this.getMessage();
  },
};
</script>