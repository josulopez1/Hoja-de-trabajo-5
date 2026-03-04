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
    plt.legend()
    plt.show()
