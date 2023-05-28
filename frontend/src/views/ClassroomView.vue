<script setup lang="ts">
import { fetch } from "@/api";
import { onUnmounted } from "vue";

const { data, abort } = fetch("classrooms").get();
onUnmounted(abort);
</script>

<template>Welcome to the Classroom View !</template>
