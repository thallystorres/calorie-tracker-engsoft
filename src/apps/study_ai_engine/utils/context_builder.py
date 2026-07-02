from core.ai_engine.context import BaseContextBuilder
from django.contrib.auth.models import User

class StudyContextBuilder(BaseContextBuilder):
    def __init__(self, user: User | None = None):
        super().__init__()
        self.user = user

    def add_profile_data(self):
        profile = getattr(self.user, "study_profile", None)
        if profile:
            self.context["objetivo"] = profile.get_goal_display()
        return self

    def add_history_and_notes(self):
        if not self.user:
            return self

        recent_items = self.user.study_sessions.prefetch_related('items__content').order_by('-timestamp')[:20]
        anotacoes = []
        for session in recent_items:
            for item in session.items.all():
                if item.notes:
                    anotacoes.append(f"[{item.content.name}]: {item.notes}")

        self.context["anotacoes"] = "\n".join(anotacoes) if anotacoes else "Nenhuma anotação."
        return self
