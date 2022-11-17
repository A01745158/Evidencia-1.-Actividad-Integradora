using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

[Serializable]
public class AgentData
{
    public string id;
    public float x, y, z;

    public AgentData(string id, float x, float y, float z)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
    }
}


[Serializable]

public class AgentsData
{
    public List<AgentData> positions;

    public AgentsData() => this.positions = new List<AgentData>();
}


public class AgentController : MonoBehaviour
{
    // Ruta de la nube
    // private string url = "https://agents.us-south.cf.appdomain.cloud/";
    string serverUrl = "http://localhost:8585";
    // Endpoints (que coincidan nombres)
    string getAgentsEndpoint = "/getAgents";
    string getObstaclesEndpoint = "/getObstacles";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";
    AgentsData agentsData, obstacleData;
    Dictionary<string, GameObject> agents;
    Dictionary<string, Vector3> prevPositions, currPositions;

    bool updated = false, started = false;

    // Una celda es una unidad de Unity
    public GameObject agentPrefab, obstaclePrefab, floor;
    public int NBoxes, width, height;
    public float timeToUpdate = 5.0f;
    private float timer, dt;

    void Start()
    {
        // Creación de objetos base
        agentsData = new AgentsData();
        obstacleData = new AgentsData();

        prevPositions = new Dictionary<string, Vector3>();
        currPositions = new Dictionary<string, Vector3>();

        agents = new Dictionary<string, GameObject>();

        floor.transform.localScale = new Vector3((float)width / 10, 1, (float)height / 10);
        floor.transform.localPosition = new Vector3((float)width / 2 - 0.5f, 0, (float)height / 2 - 0.5f);

        timer = timeToUpdate;

        // Permite iniciar una función que corre de manera concurrente (mismo tiempo que la principal)
        StartCoroutine(SendConfiguration());
    }

    private void Update()
    {   // Sirve para hacer solicitud de nuevas posiciones
        if (timer < 0)
        {
            timer = timeToUpdate;
            updated = false;
            StartCoroutine(UpdateSimulation());
        }
        // Si ya actualicé posiciones de mis agentes
        if (updated)
        {
            timer -= Time.deltaTime;
            dt = 1.0f - (timer / timeToUpdate);

            foreach (var agent in currPositions)
            {
                Vector3 currentPosition = agent.Value;
                Vector3 previousPosition = prevPositions[agent.Key];
                // Interpolación lineal para que se mueva poco a poco hasta la dirección final
                Vector3 interpolated = Vector3.Lerp(previousPosition, currentPosition, dt);
                // Resta de vectores
                Vector3 direction = currentPosition - interpolated;

                agents[agent.Key].transform.localPosition = interpolated;
                if (direction != Vector3.zero) agents[agent.Key].transform.rotation = Quaternion.LookRotation(direction);
            }
            // Interpolación
            // float t = (timer / timeToUpdate);
            // dt = t * t * ( 3f - 2f*t);
        }
    }

    IEnumerator UpdateSimulation()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + updateEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            StartCoroutine(GetAgentsData());
        }
    }
    // Configuración inicial se pone en el editor de unity y se manda a flask
    IEnumerator SendConfiguration()
    {
        // Se manda la info a través de una forma
        WWWForm form = new WWWForm();

        // deben llamarse igual. Salen del editor de Unity. En mesa deben llamarse como el String
        form.AddField("NBoxes", NBoxes.ToString());
        form.AddField("width", width.ToString());
        form.AddField("height", height.ToString());

        // Se manda un post
        UnityWebRequest www = UnityWebRequest.Post(serverUrl + sendConfigEndpoint, form);
        www.SetRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        //Aquí manda el web request
        yield return www.SendWebRequest();
        //Aquí ya terminó la corutina
        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            // se mandan 2 co-rutinas
            Debug.Log("Configuration upload complete!");
            Debug.Log("Getting Agents positions");
            StartCoroutine(GetAgentsData());
            StartCoroutine(GetObstacleData());
        }
    }

    IEnumerator GetAgentsData()
    {   //obtener nuevas posiciones de los agentes
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getAgentsEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            //Para ver JSON
            // Debug.Log(www.downloadHandler.text)
            agentsData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            foreach (AgentData agent in agentsData.positions)
            {
                Vector3 newAgentPosition = new Vector3(agent.x, agent.y, agent.z);

                if (!started)
                {   // si es la primera vez que se ejecuta
                    prevPositions[agent.id] = newAgentPosition;
                    //guarda referencia al agente nuevo en la posicion inicial 
                    agents[agent.id] = Instantiate(agentPrefab, newAgentPosition, Quaternion.identity);
                }
                else
                {   // no es la 1ª vez
                    Vector3 currentPosition = new Vector3();
                    if (currPositions.TryGetValue(agent.id, out currentPosition))
                        prevPositions[agent.id] = currentPosition;
                    currPositions[agent.id] = newAgentPosition;
                }
            }

            updated = true;
            if (!started) started = true;
        }
    }

    IEnumerator GetObstacleData()
    {
        // Posiciones de los agentes obstáculos
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getObstaclesEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            obstacleData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            Debug.Log(obstacleData.positions);

            foreach (AgentData obstacle in obstacleData.positions)
            {
                // Crear los prefabs. Agregar objetos nuevos a Unity
                Instantiate(obstaclePrefab, new Vector3(obstacle.x, obstacle.y, obstacle.z), Quaternion.identity);
            }
        }
    }
}


