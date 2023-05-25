<script setup lang="ts">
import { fetch } from "@/api";

const { data } = fetch("classrooms").get();
</script>

<template>Welcome to the Classroom View !</template>
