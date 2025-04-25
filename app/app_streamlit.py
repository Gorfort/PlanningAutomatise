import streamlit as st
import pandas as pd
from collections import defaultdict
from constraint import Problem, AllDifferentConstraint
from datetime import datetime

st.set_page_config(page_title="Planning par créneau", layout="wide")
st.title("📅 Planning intelligent avec gestion dynamique des créneaux et employés")

def parse_time(t): return datetime.strptime(t, "%H:%M")
def get_time_of_day(start): return "matin" if int(start.split(":")[0]) < 12 else "apres-midi"

jours_semaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
moments = ["matin", "apres-midi"]

# Sélection des jours/moments
st.subheader("🧭 Sélection des jours et créneaux à planifier")
selected_dayparts = {}
with st.form("daypart_form"):
    for jour in jours_semaine:
        col1, col2 = st.columns(2)
        matin = col1.checkbox(f"{jour} matin", value=True, key=f"{jour}_matin")
        aprem = col2.checkbox(f"{jour} après-midi", value=True, key=f"{jour}_aprem")
        parts = []
        if matin: parts.append("matin")
        if aprem: parts.append("apres-midi")
        if parts:
            selected_dayparts[jour] = parts
    submitted = st.form_submit_button("✅ Appliquer la sélection")

# Données par défaut
if "employees" not in st.session_state:
    st.session_state["employees"] = {
        "Alice": {"weekly_hours": 20, "days_off": [], "vacation_days": [], "assigned_days": []},
        "Bob": {"weekly_hours": 30, "days_off": [], "vacation_days": [], "assigned_days": []},
        "Charlie": {"weekly_hours": 40, "days_off": [], "vacation_days": [], "assigned_days": []}
    }

if "business_schedule" not in st.session_state:
    st.session_state["business_schedule"] = {
        "Lundi": [("08:00", "12:00"), ("14:00", "18:00")],
        "Mardi": [("08:00", "12:00"), ("14:00", "18:00")],
        "Mercredi": [("08:00", "12:00")],
        "Jeudi": [("08:00", "12:00"), ("14:00", "18:00")],
        "Vendredi": [("08:00", "12:00"), ("14:00", "18:00")],
        "Samedi": [("09:00", "13:00"), ("14:00", "18:00")],
        "Dimanche": [("10:00", "14:00"), ("14:00", "18:00")]
    }

if "required_employees_per_day" not in st.session_state:
    st.session_state["required_employees_per_day"] = {j: 1 for j in jours_semaine}

# Horaires
with st.expander("🔧 Réglages des horaires et besoins", expanded=False):
    with st.form("horaires_form"):
        for day in selected_dayparts:
            st.markdown(f"### 📆 {day}")
            for i, (start, end) in enumerate(st.session_state["business_schedule"].get(day, [])):
                moment = get_time_of_day(start)
                if moment not in selected_dayparts[day]:
                    continue
                col1, col2 = st.columns(2)
                with col1:
                    st.time_input(f"{day}_{moment}_start_{i}", value=datetime.strptime(start, "%H:%M").time(), key=f"{day}_{moment}_start_{i}")
                with col2:
                    st.time_input(f"{day}_{moment}_end_{i}", value=datetime.strptime(end, "%H:%M").time(), key=f"{day}_{moment}_end_{i}")
            st.session_state["required_employees_per_day"][day] = st.slider(f"👥 Besoin en personnel {day}", 0, 5, st.session_state["required_employees_per_day"].get(day, 1))
        st.form_submit_button("✅ Mettre à jour les horaires")

# Employés dynamiques
with st.expander("👥 Gestion des employés", expanded=True):
    with st.form("employees_form"):
        for name in list(st.session_state["employees"].keys()):
            emp = st.session_state["employees"][name]
            st.markdown(f"#### 👤 {name}")
            emp["weekly_hours"] = st.slider(f"{name} - Heures contrat", 0, 60, emp["weekly_hours"], key=f"{name}_hrs")
            emp["days_off"] = st.multiselect(f"{name} - Jours off", jours_semaine, default=emp["days_off"], key=f"{name}_off")
            emp["vacation_days"] = st.multiselect(f"{name} - Vacances", [(j, m) for j in selected_dayparts for m in selected_dayparts[j]], default=emp["vacation_days"], format_func=lambda x: f"{x[0]} {x[1]}", key=f"{name}_vac")
            emp["assigned_days"] = st.multiselect(f"{name} - Assignés", [(j, m) for j in selected_dayparts for m in selected_dayparts[j]], default=emp["assigned_days"], format_func=lambda x: f"{x[0]} {x[1]}", key=f"{name}_ass")
            if st.checkbox(f"🗑️ Supprimer {name}", key=f"{name}_delete"):
                del st.session_state["employees"][name]
                st.experimental_rerun()
        new_name = st.text_input("Nom du nouvel employé")
        if st.form_submit_button("✅ Mettre à jour les employés"):
            st.success("Modifications enregistrées")
        if new_name and new_name not in st.session_state["employees"]:
            if st.form_submit_button("➕ Ajouter l'employé"):
                st.session_state["employees"][new_name] = {"weekly_hours": 20, "days_off": [], "vacation_days": [], "assigned_days": []}
                st.success(f"{new_name} a été ajouté.")

# Génération du planning
def generate_multi_shifts(schedule, required, selected_dayparts):
    shifts = []
    for day, times in schedule.items():
        if day not in selected_dayparts: continue
        for start, end in times:
            moment = get_time_of_day(start)
            if moment not in selected_dayparts[day]: continue
            duration = (parse_time(end) - parse_time(start)).total_seconds() / 3600
            for i in range(required.get(day, 1)):
                shifts.append({
                    "var_name": f"{day}_{start}_{end}_poste{i+1}",
                    "day": day, "start": start, "end": end,
                    "duration_hours": duration, "moment": moment, "position": i+1
                })
    return shifts

def build_scheduler(employees, shifts):
    problem = Problem()
    for s in shifts:
        available = [e for e in employees if s["day"] not in employees[e]["days_off"] and (s["day"], s["moment"]) not in employees[e]["vacation_days"]]
        problem.addVariable(s["var_name"], available)
    groups = defaultdict(list)
    for s in shifts:
        groups[(s["day"], s["start"], s["end"])].append(s["var_name"])
    for g in groups.values():
        problem.addConstraint(AllDifferentConstraint(), g)
    def constraint_heures(*args):
        total = defaultdict(float)
        for name, sft in zip(args, shifts):
            total[name] += sft["duration_hours"]
        return all(total[n] <= employees[n]["weekly_hours"] for n in employees)
    def constraint_assignation(*args):
        assigned = defaultdict(set)
        for emp, sft in zip(args, shifts):
            assigned[emp].add((sft["day"], sft["moment"]))
        for n in employees:
            for required in employees[n]["assigned_days"]:
                if required not in assigned[n]:
                    return False
        return True
    varnames = [s["var_name"] for s in shifts]
    problem.addConstraint(constraint_heures, varnames)
    problem.addConstraint(constraint_assignation, varnames)
    return problem.getSolutions(), shifts

def select_best_solution(sols, shifts, employees):
    def score(sol):
        hrs = defaultdict(float)
        for s in shifts:
            hrs[sol[s["var_name"]]] += s["duration_hours"]
        return sum(abs(hrs[e] - employees[e]["weekly_hours"]) for e in employees)
    return min(sols, key=score) if sols else None

if st.button("🚀 Générer le planning maintenant !"):
    shifts = generate_multi_shifts(st.session_state["business_schedule"], st.session_state["required_employees_per_day"], selected_dayparts)
    solutions, shifts = build_scheduler(st.session_state["employees"], shifts)
    if solutions:
        sol = select_best_solution(solutions, shifts, st.session_state["employees"])
        df = pd.DataFrame([{
            "Jour": s["day"], "Début": s["start"], "Fin": s["end"], "Poste": s["position"],
            "Moment": s["moment"], "Employé": sol[s["var_name"]], "Durée (h)": s["duration_hours"]
        } for s in shifts])
        bilan = pd.DataFrame([{ "Employé": e, "Heures assignées": df[df["Employé"] == e]["Durée (h)"].sum(), "Contrat (h)": st.session_state["employees"][e]["weekly_hours"] } for e in st.session_state["employees"]])
        st.success("✅ Planning généré avec succès !")
        st.subheader("📅 Planning")
        st.dataframe(df)
        st.subheader("📊 Bilan")
        st.dataframe(bilan)
        st.download_button("📥 Télécharger le planning", data=df.to_csv(index=False), file_name="planning.csv")
        st.download_button("📥 Télécharger le bilan", data=bilan.to_csv(index=False), file_name="bilan_employes.csv")
    else:
        st.error("❌ Aucune solution trouvée avec les contraintes actuelles.")