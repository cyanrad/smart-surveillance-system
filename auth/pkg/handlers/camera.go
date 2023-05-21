package handlers

import (
	"encoding/json"
	"io"
	"log"
	"net/http"
	"strconv"

	"github.com/CCTVBackend/pkg/models"
	"github.com/gorilla/mux"
)

func (h handler) CreateCamera(w http.ResponseWriter, r *http.Request) {

	//Read request body
	defer r.Body.Close()
	body, err := io.ReadAll(r.Body)

	if err != nil {
		log.Fatalln(err)
	}

	var camera models.Camera

	json.Unmarshal(body, &camera)

	//add to database and check if error
	if result := h.DB.Create(&camera); result.Error != nil {
		//log error and return status BadRequest
		log.Println(result.Error)
		w.WriteHeader(http.StatusBadRequest)
		w.Header().Add("Content-Type", "application/json")
		json.NewEncoder(w).Encode("Failed")
		return
	}

	//Return status Created
	w.WriteHeader(http.StatusCreated)
	w.Header().Add("Content-Type", "application/json")
	data, err := json.Marshal(&camera)
	if err != nil {
		log.Println(err)
	}
	w.Write(data)
}

func (h handler) ReadCamera(w http.ResponseWriter, r *http.Request) {

	//Get id from URL
	vars := mux.Vars(r)
	id, _ := strconv.Atoi(vars["id"])

	var camera models.Camera
	// find camera in db
	if result := h.DB.First(&camera, id); result.Error != nil {
		//log error and return status BadRequest
		log.Println(result.Error)
		w.WriteHeader(http.StatusBadRequest)
		w.Header().Add("Content-Type", "application/json")
		json.NewEncoder(w).Encode("Failed")
		return
	}
	//remove owner from camera

	//Return status Created
	w.WriteHeader(http.StatusOK)
	w.Header().Add("Content-Type", "application/json")
	json.NewEncoder(w).Encode(camera)
}

func (h handler) UpdateCamera(w http.ResponseWriter, r *http.Request) {
	//Get Id from URL,
	vars := mux.Vars(r)
	id, _ := strconv.Atoi(vars["id"])

	//Read request body
	body, err := io.ReadAll(r.Body)
	if err != nil {
		log.Fatalln(err)
	}

	var camera models.Camera
	//Find camera in DB
	result := h.DB.First(&camera, id)
	if result.Error != nil {
		//log error and return status BadRequest
		log.Println(result.Error)
		w.WriteHeader(http.StatusBadRequest)
		w.Header().Add("Content-Type", "application/json")
		json.NewEncoder(w).Encode("Failed")
		return
	}

	//Overwrite camera data
	var newCamera models.Camera
	json.Unmarshal(body, &newCamera)
	camera = newCamera

	//make sure id doesnt change (to avoid dupes)
	camera.ID = uint64(id)

	//Push changes to DB
	h.DB.Save(&camera)

	//return ok
	w.WriteHeader(http.StatusOK)
	w.Header().Add("Content-Type", "application/json")
	json.NewEncoder(w).Encode("Updated")

}
func (h handler) DeleteCamera(w http.ResponseWriter, r *http.Request) {

	//Get Id from URL,
	vars := mux.Vars(r)
	id, _ := strconv.Atoi(vars["id"])

	var camera models.Camera

	//Find camera in DB
	result := h.DB.First(&camera, id)
	if result.Error != nil {
		//log error and return status BadRequest
		log.Println(result.Error)
		w.WriteHeader(http.StatusBadRequest)
		w.Header().Add("Content-Type", "application/json")
		json.NewEncoder(w).Encode("Failed")
		return
	}

	//Delete camera in DB
	if result := h.DB.Delete(&camera); result.Error != nil {
		//log error and return status BadRequest
		log.Println(result.Error)
		w.WriteHeader(http.StatusBadRequest)
		w.Header().Add("Content-Type", "application/json")
		json.NewEncoder(w).Encode("Failed")
		return
	}

	//return ok
	w.WriteHeader(http.StatusOK)
	w.Header().Add("Content-Type", "application/json")
	json.NewEncoder(w).Encode("Deleted")

}
