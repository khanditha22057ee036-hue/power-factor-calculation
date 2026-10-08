"""
Power Factor Calculator
-----------------------
A menu-driven program for engineering students to calculate the power
factor of single-phase AC circuits and to design power factor correction.

Key relations:
    Power factor   pf = cos(phi) = P / S
    Apparent power S  = V * I                (VA)
    Active power   P  = V * I * cos(phi)     (W)
    Reactive power Q  = V * I * sin(phi)     (VAR)
    Power triangle S^2 = P^2 + Q^2

Series R-L / R-C circuit:
    Z = sqrt(R^2 + X^2),   pf = R / Z

Power factor correction:
    Qc = P * (tan(phi1) - tan(phi2))
    C  = Qc / (2 * pi * f * V^2)

    Lagging pf -> inductive load (motors, transformers)
    Leading pf -> capacitive load
"""

import math


# ---------------------------------------------------------------- input helpers
def get_positive_float(prompt):
    """Keep asking until the user enters a valid positive number."""
    while True:
        try:
            value = float(input(prompt))
            if value <= 0:
                print("  Please enter a value greater than zero.")
                continue
            return value
        except ValueError:
            print("  Invalid input. Please enter a number.")


def get_power_factor(prompt="Power factor (0 to 1): "):
    """Ask for a power factor between 0 (exclusive) and 1 (inclusive)."""
    while True:
        pf = get_positive_float(prompt)
        if pf <= 1:
            return pf
        print("  Power factor cannot be greater than 1.")


# ------------------------------------------------------------------ core maths
def pf_from_p_s(p, s):
    """pf = P / S"""
    return p / s


def pf_from_p_q(p, q):
    """pf = P / sqrt(P^2 + Q^2)"""
    return p / math.sqrt(p ** 2 + q ** 2)


def pf_from_vip(v, i, p):
    """pf = P / (V * I)"""
    return p / (v * i)


def pf_from_r_x(r, x):
    """Series circuit: pf = R / sqrt(R^2 + X^2)"""
    return r / math.sqrt(r ** 2 + x ** 2)


def pf_from_angle(angle_deg):
    """pf = cos(phi)"""
    return math.cos(math.radians(angle_deg))


def power_triangle(p, pf):
    """Return (S, Q) when P and pf are known."""
    s = p / pf
    q = math.sqrt(max(s ** 2 - p ** 2, 0))
    return s, q


def required_kvar(p_kw, pf_old, pf_new):
    """Qc = P * (tan(phi1) - tan(phi2))  in kVAR"""
    return p_kw * (math.tan(math.acos(pf_old)) - math.tan(math.acos(pf_new)))


def capacitance_needed(qc_kvar, v, f):
    """C = Qc / (2 * pi * f * V^2), returned in microfarads."""
    c = (qc_kvar * 1000) / (2 * math.pi * f * v ** 2)
    return c * 1e6


# ------------------------------------------------------------------- display
def rating(pf):
    """Short comment on how good the power factor is."""
    if pf >= 0.95:
        return "Excellent"
    if pf >= 0.90:
        return "Good"
    if pf >= 0.80:
        return "Acceptable, correction recommended"
    return "Poor, correction strongly recommended"


def show_pf(pf, load_type=None):
    """Print the power factor, angle and comment."""
    print("\n  ----- Results -----")
    print(f"  Power factor = {pf:.4f}")
    print(f"  Phase angle  = {math.degrees(math.acos(pf)):.2f} degrees")
    if load_type:
        print(f"  Nature       = {load_type}")
    print(f"  Remark       = {rating(pf)}")


def ask_load_type():
    """Ask whether the load is inductive or capacitive."""
    while True:
        t = input("Load type - (L)agging inductive or (C) leading capacitive: ").strip().lower()
        if t in ("l", "lagging"):
            return "Lagging (inductive load)"
        if t in ("c", "leading"):
            return "Leading (capacitive load)"
        print("  Please enter L or C.")


def menu():
    print("\n" + "=" * 52)
    print("           POWER FACTOR CALCULATOR")
    print("=" * 52)
    print(" 1. From active power P and apparent power S")
    print(" 2. From active power P and reactive power Q")
    print(" 3. From voltage V, current I and power P")
    print(" 4. From resistance R and reactance X (series)")
    print(" 5. From phase angle")
    print(" 6. Power triangle (P and power factor)")
    print(" 7. Power factor correction (capacitor size)")
    print(" 0. Exit")
    print("-" * 52)


def main():
    while True:
        menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            p = get_positive_float("Active power P (W): ")
            s = get_positive_float("Apparent power S (VA): ")
            if p > s:
                print("  P cannot be greater than S.")
            else:
                show_pf(pf_from_p_s(p, s), ask_load_type())

        elif choice == "2":
            p = get_positive_float("Active power P (W): ")
            q = get_positive_float("Reactive power Q (VAR): ")
            show_pf(pf_from_p_q(p, q), ask_load_type())

        elif choice == "3":
            v = get_positive_float("Voltage V (V): ")
            i = get_positive_float("Current I (A): ")
            p = get_positive_float("Active power P (W): ")
            if p > v * i:
                print("  P cannot be greater than V x I. Check your values.")
            else:
                show_pf(pf_from_vip(v, i, p), ask_load_type())

        elif choice == "4":
            r = get_positive_float("Resistance R (ohm): ")
            x = get_positive_float("Reactance X (ohm): ")
            kind = ask_load_type()
            show_pf(pf_from_r_x(r, x), kind)

        elif choice == "5":
            angle = get_positive_float("Phase angle (degrees, up to 90): ")
            if angle > 90:
                print("  Angle must be 90 degrees or less.")
            else:
                show_pf(pf_from_angle(angle), ask_load_type())

        elif choice == "6":
            p = get_positive_float("Active power P (W): ")
            pf = get_power_factor()
            s, q = power_triangle(p, pf)
            print("\n  ----- Power Triangle -----")
            print(f"  Active power   P = {p:,.2f} W")
            print(f"  Apparent power S = {s:,.2f} VA")
            print(f"  Reactive power Q = {q:,.2f} VAR")

        elif choice == "7":
            p_kw = get_positive_float("Load active power (kW): ")
            pf_old = get_power_factor("Existing power factor: ")
            pf_new = get_power_factor("Desired power factor: ")
            if pf_new <= pf_old:
                print("  Desired power factor must be higher than the existing one.")
            else:
                v = get_positive_float("Supply voltage (V): ")
                f = get_positive_float("Frequency (Hz): ")
                qc = required_kvar(p_kw, pf_old, pf_new)
                print("\n  ----- Correction -----")
                print(f"  Capacitor rating Qc = {qc:.2f} kVAR")
                print(f"  Capacitance C       = {capacitance_needed(qc, v, f):,.2f} microfarad (single phase)")

        elif choice == "0":
            print("\nThank you for using the calculator. Goodbye!")
            break

        else:
            print("  Invalid choice. Please select from the menu.")


if __name__ == "__main__":
    main()
