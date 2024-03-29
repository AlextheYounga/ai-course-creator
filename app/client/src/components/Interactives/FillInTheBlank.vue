<template>
    <div>
        <p class="text-xl">Question: {{ this.data.question }}</p>
        <input class="text-gray-700 w-full rounded-md mb-4" :value="this.data.answer"></input>
    </div>
</template>

<script>
export default {
    name: 'FillInTheBlank',
    props: {
        data: {
            type: Object,
            required: true,
        }
    },
};
</script>