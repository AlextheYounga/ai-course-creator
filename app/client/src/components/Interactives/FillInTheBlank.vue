<template>
    <div>
        <p class="font-bold text-xl">Question: {{ this.interactive.data.question }}</p>
        <input class="text-gray-700 w-full rounded-md mb-4" :value="this.interactive.data.answer"></input>
    </div>
</template>

<script>
export default {
    name: 'FillInTheBlank',
    props: {
        interactive: {
            type: Object,
            required: true,
        }
    },
};
</script>