<template>
    <pre>
       <code :class="`language-${this.data.language}`">
              {{ this.data.content }}
       </code>
    </pre>
</template>

<script>
import hljs from 'highlight.js';
export default {
    name: 'CodeEditor',
    props: {
        data: {
            type: Object,
            required: true,
        }
    },
    mounted() {
        hljs.highlightAll();
    }
};
</script>
