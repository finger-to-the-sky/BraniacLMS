class CoursesDetailView(TemplateView):
    template_name = "mainapp/courses_detail.html"

    def get_context_data(self, pk=None, **kwargs):
        logger.debug("Yet another log message")
        context = super(CoursesDetailView, self).get_context_data(**kwargs)
        context["course_object"] = get_object_or_404(mainapp_models.Courses, pk=pk)
        context["lessons"] = mainapp_models.Lesson.objects.filter(course=context["course_object"])
        context["teachers"] = mainapp_models.CourseTeachers.objects.filter(course=context["course_object"])
        if not self.request.user.is_anonymous:
            if not mainapp_models.CourseFeedback.objects.filter(
                course=context["course_object"], user=self.request.user
            ).count():
                context["feedback_form"] = mainapp_forms.CourseFeedbackForm(
                    course=context["course_object"], user=self.request.user
                )

        cached_feedback = cache.get(f"feedback_list_{pk}")
        if not cached_feedback:
            context["feedback_list"] = (
                mainapp_models.CourseFeedback.objects.filter(course=context["course_object"])
                .order_by("-created", "-rating")[:5]
                .select_related()
            )
            cache.set(f"feedback_list_{pk}", context["feedback_list"], timeout=300)  # 5 minutes

            # Archive object for tests --->
            import pickle

            with open(f"mainapp/fixtures/005_feedback_list_{pk}.bin", "wb") as outf:
                pickle.dump(context["feedback_list"], outf)
            # <--- Archive object for tests

        else:
            context["feedback_list"] = cached_feedback

        return context