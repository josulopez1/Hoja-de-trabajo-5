import simpy
import random
import statistics
import matplotlib.pyplot as plt

RANDOM_SEED = 42


def proceso(env, nombre, ram, cpu, instrucciones_por_ciclo, tiempos):

    llegada = env.now

    memoria = random.randint(1, 10)
    instrucciones = random.randint(1, 10)

    # pedir memoria
    yield ram.get(memoria)

    while instrucciones > 0:

        with cpu.request() as req:
            yield req

            ejecutadas = min(instrucciones_por_ciclo, instrucciones)
            yield env.timeout(1)
            instrucciones -= ejecutadas

        # posible I/O
        if instrucciones > 0:
            if random.randint(1, 21) == 1:
                yield env.timeout(1)

    # devolver memoria
    yield ram.put(memoria)

    tiempos.append(env.now - llegada)


def generar(env, ram, cpu, instrucciones_por_ciclo, intervalo, cantidad, tiempos):
    for i in range(cantidad):
        yield env.timeout(random.expovariate(1.0 / intervalo))
        env.process(proceso(env, f"P{i}", ram, cpu, instrucciones_por_ciclo, tiempos))


def simular(n_procesos, intervalo, memoria=100, velocidad_cpu=3, cpus=1):

    random.seed(RANDOM_SEED)

    env = simpy.Environment()
    ram = simpy.Container(env, init=memoria, capacity=memoria)
    cpu = simpy.Resource(env, capacity=cpus)

    tiempos = []

    env.process(generar(env, ram, cpu, velocidad_cpu, intervalo, n_procesos, tiempos))
    env.run()

    promedio = statistics.mean(tiempos)
    desviacion = statistics.stdev(tiempos) if len(tiempos) > 1 else 0

    return promedio, desviacion


if __name__ == "__main__":

    cantidades = [25, 50, 100, 150, 200]
    intervalos = [10, 5, 1]

    # -------------------------
    # Parte 1: intervalos base
    # -------------------------
    plt.figure()

    for intervalo in intervalos:

        promedios = []

        print(f"\nIntervalo = {intervalo}")
        print("Procesos | Promedio | Desviacion")

        for n in cantidades:
            prom, des = simular(n, intervalo)
            promedios.append(prom)
            print(f"{n:8} | {prom:.2f} | {des:.2f}")

        plt.plot(cantidades, promedios, label=f"Intervalo {intervalo}")

    plt.xlabel("Numero de procesos")
    plt.ylabel("Tiempo promedio")
    plt.title("Tiempo promedio vs Numero de procesos")
    plt.legend()
    plt.show()

    # -------------------------
    # Parte 2: estrategias (intervalo = 1)
    # -------------------------
    print("\n--- Estrategias con intervalo = 1 ---")

    plt.figure()

    # RAM 200
    promedios_ram = []
    print("\nMemoria 200")
    for n in cantidades:
        prom, _ = simular(n, 1, memoria=200)
        promedios_ram.append(prom)
        print(n, prom)

    plt.plot(cantidades, promedios_ram, label="RAM 200")

    # CPU mas rapido
    promedios_cpu = []
    print("\nCPU mas rapido (6 instrucciones)")
    for n in cantidades:
        prom, _ = simular(n, 1, velocidad_cpu=6)
        promedios_cpu.append(prom)
        print(n, prom)

    plt.plot(cantidades, promedios_cpu, label="CPU mas rapido")

    # 2 CPUs
    promedios_2cpu = []
    print("\n2 CPUs")
    for n in cantidades:
        prom, _ = simular(n, 1, cpus=2)
        promedios_2cpu.append(prom)
        print(n, prom)

    plt.plot(cantidades, promedios_2cpu, label="2 CPUs")

    plt.xlabel("Numero de procesos")
    plt.ylabel("Tiempo promedio")
    plt.title("Comparacion de estrategias (Intervalo 1)")
    plt.legend()
    plt.show()
