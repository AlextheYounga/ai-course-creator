<template>
    <pre>
       <code :class="`language-${this.data.language}`">
              {{ this.data.content }}
       </code>
    </pre>
</template>

<script>
export default {
    name: 'CodeEditor',
    props: {
        data: {
            type: Object,
            required: true,
        }
    },
};
</script>
